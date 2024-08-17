# Project Name: AggieAdvisor

## Description
AggieAdvisor is an innovative open-source platform designed to enhance the course registration experience for students.
By integrating with the RAG system, AggieAdvisor provides real-time access to registration information while ensuring data privacy and restricted access through controlled gates for any connected machine learning models.

## Features

### Minimum Viable Product (MVP)
- **Course Registration Information**: Access real-time registration data within the RAG system.
- **Control Gates for LLM**: Ensures that the connected machine learning models do not access additional unauthorized information.

### Additional Features
- **Course Details**: Fetch course descriptions, prerequisites, and information about the professors.
- **RMP Insights**: Leverage RateMyProfessors (RMP) to extract and analyze professor reviews and ratings.
- **Grade Distributions**: View grade statistics for specific courses and professors to aid in informed decision making.

### Cool Ideas (Future Scope)
- **Course Recommender System**: Develop an intelligent recommender system to suggest courses based on student history and preferences.
- **Availability Checks**: Integrate course availability features that interact with the course recommender for enhanced planning.
- **Extended Feature Integration**: Expand the platform's capabilities based on user feedback and technological advancements.

## Installation
To set up AggieAdvisor using Docker, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rushiljay/Aggie-Course-Recommender.git
   ```

2. **Build the Docker image:**
   Navigate to the project directory and build the Docker image using the provided Dockerfile:
   ```bash
   docker-compose up --build .
   ```

## Usage
After building the Docker image, you can run and access the application:

1. **Access the application:**
   The application will be running inside the Docker container. You can interact with it directly from the command line that appears after you start the container.
   ```bash
   docker-compose run app /bin/bash
   ```

For more detailed usage and additional configurations, please refer to the documentation provided in the `/docs` folder.
Use pdoc to create additional documentation

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Project Link: [https://github.com/rushiljay/Aggie-Course-Recommender](https://github.com/rushiljay/Aggie-Course-Recommender)
