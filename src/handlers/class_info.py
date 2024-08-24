from bs4 import BeautifulSoup
import requests
import re
import concurrent.futures
import json


def extract_prerequisite(course_description):
    prereq_regex = r"Prerequisite[s]*:\s*(.+)"
    if "Cross Listing" in course_description:
        prereq_regex = r"Prerequisite[s]*:\s*(.+?)(?=\s*Cross Listing)"
    elif "Corequisite" in course_description:
        prereq_regex = r"Prerequisite[s]*:\s*(.+?)(?=\s*Corequisite)"

    prerequisites = re.search(prereq_regex, course_description)
    prerequisites = prerequisites.group(1).strip() if prerequisites else "None"

    return prerequisites


def extract_description(course_description):
    description_regex = (
        r"(.*(?=\s*Prerequisite))"
        if "Prerequisite" in course_description
        else r"(  .*)"
    )
    description = re.search(description_regex, course_description)
    description = description.group(0).strip() if description else "None"
    if "Cross Listing" in description:
        description_regex = r"(.*(?=\s*Cross Listing))"
        description = re.search(description_regex, description)
        description = description.group(0).strip() if description else "None"
    if re.search(
        r"^\([^0-9]", description
    ):  # if the description starts with an opening parentheses
        description_regex = r"(  .*)"
        description = re.search(description_regex, description)
        description = description.group(0).strip() if description else "None"
    if description == "None":
        description_regex = r"(\n .*)"
        description = re.search(description_regex, course_description)
        description = description.group(0).strip() if description else "None"

    return description


def extract_course_details(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # Find all course blocks
    course_blocks = soup.find_all("div", class_="courseblock")

    courses = []

    # Loop through each course block and extract the details

    for course in course_blocks:
        title = course.find("h2", class_="courseblocktitle").text.strip()
        course_description = course.find("p", class_="courseblockdesc").text.strip()
        course_description = course_description.replace("\u00a0", " ")

        patterns = {
            "Department": r"^(.*?)\s+\d+",
            "Course Number": r"^[^\d]*(\d+)",
            "Course Name": r".*\d+\s*(.*)",
            "Credits": r"Credit[s]*\s+(\d+\s*(?:to|-)\s*\d+|\d+)",
            "Lecture Hours": r"(\d+\s*(?:to|-)\s*\d+|\d+)\s+Lecture Hour[s]*",
            "Lab Hours": r"(\d+\s*(?:to|-)\s*\d+|\d+)\s+Lab Hour[s]*",
            "Other Hours": r"(\d+\s*(?:to|-)\s*\d+|\d+)\s+Other Hour[s]*",
            "Corequisites": r"Corequisite[s]:\s*(.+)",
            "Cross Listing": r"Cross Listing:\s*(.+)",
        }

        results = {}

        def parallel_regex_search(pattern, string, default):
            match = re.search(pattern, string)
            return match.group(1).strip() if match else default

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(patterns)
        ) as executor:
            future_to_key = {
                executor.submit(
                    parallel_regex_search,
                    patterns[key],
                    course_description
                    if key not in {"Department", "Course Number", "Course Name"}
                    else title,
                    "Not specified",
                ): key
                for key in patterns
            }
            for future in future_to_key:
                key = future_to_key[future]
                results[key] = future.result()

        results["Prerequisites"] = extract_prerequisite(course_description)
        results["Description"] = extract_description(course_description)

        courses.append(results)

    return courses


def fetch_course_details(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        return extract_course_details(response.text)
    return []


def get_department_courses(department: str):
    urls = {
        "Undergraduate": f"https://catalog.tamu.edu/undergraduate/course-descriptions/{department.lower()}/",
        "Graduate": f"https://catalog.tamu.edu/graduate/course-descriptions/{department.lower()}/",
    }

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_url = {
            executor.submit(fetch_course_details, url): name
            for name, url in urls.items()
        }
        results = {}
        for future in future_to_url:
            result = future.result()
            results[future_to_url[future]] = result
    return results


def get_departments():
    link = f"https://howdy.tamu.edu/api/course-sections"
    res = requests.post(
        link, json={"startRow": 0, "endRow": 0, "termCode": 202431, "publicSearch": "Y"}
    )

    res = res.json()

    departments = set()

    for course in res:
        departments.add(course["SWV_CLASS_SEARCH_SUBJECT"])

    return departments


def get_courses_for_subject(department):
    courses = get_department_courses(department)
    return department, courses


def get_all_courses():
    departments = list(get_departments())

    departments.sort()

    courses = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Map the function and subjects to the executor
        future_to_department = {
            executor.submit(get_courses_for_subject, department): department
            for department in departments
        }

        # As each future completes, store the result in the courses dictionary
        for future in concurrent.futures.as_completed(future_to_department):
            department, department_courses = future.result()
            courses[department] = department_courses

    return courses


# prompt: export courses as a pretty json file

if __name__ in "__main__":
    with open("courses.json", "w") as f:
        json.dump(get_all_courses(), f, indent=4)
