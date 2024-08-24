# TODO: rename this

import langgraph


""""
Rag pipeline:

question
get crn and term

throw error if no crn, no term is assumed to be term
fall is assumed to be fall 2024, default is fall 2024

fall 2024 = 202431

yyyy+(1 if spring, 2 if summer, and 3 if fall)+(1 if tamu, 2 if galveston)

then scrap course, return requested information

provide current year, and month

if data can't be found make sure user knows

prevent misuse of llm, only to specific purpose

# make bot scrape prev historical professor evals

have multiple agents:
- one gets the term and crn
- gets output from tool
- checks for llm safety, and fit to question
"""

"""
develop a tool that looks at the different course evals based on CRN and term number
"""
