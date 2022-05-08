"""
Inside conditions.json, you will see a subset of UNSW courses mapped to their 
corresponding text conditions. We have slightly modified the text conditions
to make them simpler compared to their original versions.

Your task is to complete the is_unlocked function which helps students determine 
if their course can be taken or not. 

We will run our hidden tests on your submission and look at your success rate.
We will only test for courses inside conditions.json. We will also look over the 
code by eye.

NOTE: We do not expect you to come up with a perfect solution. We are more interested
in how you would approach a problem like this.
"""
import json
import re
import sys

COURSE_CODE_REGEX = r'([A-Z]{4}|)[0-9]{4}'

# NOTE: DO NOT EDIT conditions.json
with open("./conditions.json") as f:
    CONDITIONS = json.load(f)
    f.close()


def custom_split(s: str) -> list:
    '''
    Splits an uppercase string into:
        course codes, "AND", "OR", items contained in brackets, uoc requirements
    '''
    # First split normally to then rejoin certain items
    simple = s.split()

    result = []
    curr_start = 0
    curr_end = 0
    while curr_end <= len(simple):
        curr = ' '.join(simple[curr_start:curr_end]).strip(" .,")
        if "UNITS" in curr:
            # If this is a uoc requirement, loop until its end
            while curr_end < len(simple) and (simple[curr_end] not in ["OR", "AND"]):
                curr_end += 1
            result.append(' '.join(simple[curr_start:curr_end]).strip(" .,"))
            curr_start = curr_end
        elif '(' in curr:
            # If this an item in brackets, loop to find its closing bracket
            while curr_end < len(simple) and not is_closed(simple[curr_start:curr_end]):
                curr_end += 1
            result.append(' '.join(simple[curr_start:curr_end]).strip(" .,"))
            curr_start = curr_end
        elif curr == "AND" or re.fullmatch(COURSE_CODE_REGEX, curr):
            # These are separate items
            result.append(curr)
            curr_start = curr_end
        elif curr == "OR":
            # Unnecessary
            curr_start = curr_end

        curr_end += 1

    return result


def parse_prereqs(conditions: str) -> list:
    """
    Parse a given condition string into a condition list
    Each item is a list representing separate AND conditions (all must be met)
    Each AND condition list represents a set of OR conditions (at least one must be met)
    The item lists may contain:
        - A string, which must be a substring of one of the student's courses
        - A tuple of form (int, [str]), the student must have at least int amount of
          courses containing any of the strings in the list
        - A condition list of the same form
    """
    # Format: uppercase and remove the leading "Prereqs:" or similar from string
    conditions = conditions.upper()
    conditions = conditions[conditions.find(':') + 1:]

    # Split
    conditions = custom_split(conditions)

    # Assemble as described in docstring
    prereqs = []
    curr_and = []
    for cond in conditions:
        if cond == 'AND':
            # End the current prereq and start a new one
            prereqs.append(curr_and)
            curr_and = []
        elif re.fullmatch(COURSE_CODE_REGEX, cond):
            # Add course codes as is
            curr_and.append(cond)
        elif cond[0] == '(' and cond[-1] == ')':
            # Parse any nested conditions
            curr_and.append(parse_prereqs(cond[1:-1]))
        elif "UNITS" in cond:
            # Parse any UOC based conditions
            curr_and.append(parse_uoc_condition(cond))
    if curr_and != []:
        prereqs.append(curr_and)

    return prereqs


def parse_uoc_condition(s: str) -> tuple:
    '''
    Given a string detailing a UOC condition, return a tuple of the form:
        (# of subjects required, list of substrings that requried subjects contain)
    '''
    split = s.split()
    uoc_required = int(split[split.index("UNITS") - 1])
    uoc_conditions = []
    if "IN" in s:
        # If there are further conditions on UOC
        if "LEVEL" in s:
            # Courses from a given level and discipline
            level_idx = split.index("LEVEL")
            uoc_conditions.append(
                split[level_idx + 2] + split[level_idx + 1])
        elif "COURSES" in s:
            # Courses from a given discipline
            uoc_conditions.append(split[split.index("COURSES") - 1])
        else:
            # List of specific courses
            for course in split[split.index("IN") + 1:]:
                uoc_conditions.append(course.strip("( ).,"))
    else:
        uoc_conditions.append("")

    return (uoc_required // 6, uoc_conditions)


def is_closed(strings: list) -> bool:
    '''
    Given an ordered list of strings, return whether or not all brackets are closed
    '''
    return sum(s.count('(') for s in strings) == sum(s.count(')') for s in strings)


def meets_prereq(courses_list: list, prereq: list) -> bool:
    '''
    Return if the given courses list satisfies the given prereq
    A prereq is a list of criteria where at least one must be satisfied
    '''
    # Loop through all items and return True if any are met
    for item in prereq:
        if isinstance(item, str):
            # If it is a string, check if any course in courses list is substring
            if any(item in course for course in courses_list):
                return True
        elif isinstance(item, tuple):
            # If it is a tuple, count the number of courses that contain one of the target strings
            num, strings = item
            if sum(any(s in course for s in strings) for course in courses_list) >= num:
                return True
        elif isinstance(item, list):
            # If it is a list, recursively check it
            if all(meets_prereq(courses_list, p) for p in item):
                return True

    return False


def is_unlocked(courses_list: list, target_course: str) -> bool:
    """Given a list of course codes a student has taken, return true if the target_course
    can be unlocked by them.
    You do not have to do any error checking on the inputs and can assume that
    the target_course always exists inside conditions.json
    You can assume all courses are worth 6 units of credit
    """
    prereqs = parse_prereqs(CONDITIONS[target_course])
    return all(meets_prereq(courses_list, prereq) for prereq in prereqs)


if __name__ == '__main__':
    pass
