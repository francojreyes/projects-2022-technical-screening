"""
Inside conditions.json, you will see a subset of UNSW courses mapped to their
corresponding text conditions. We have slightly modified the text conditions
to make them simpler compared to their original versions.

Your task is to complete the is_unlocked function which helps students determine
if their course can be taken or not.

We will run our hidden tests on your submission and look at your success rate.
We will only test for courses inside conditions.json. We will also look over the
code by eye.

NOTE: This challenge is EXTREMELY hard and we are not expecting anyone to pass all
our tests. In fact, we are not expecting many people to even attempt this.
For complete transparency, this is worth more than the easy challenge.
A good solution is favourable but does not guarantee a spot in Projects because
we will also consider many other criteria.
"""
import json

# NOTE: DO NOT EDIT conditions.json
with open("./conditions.json") as f:
    CONDITIONS = json.load(f)
    f.close()

def parse_prereqs(conditions):
    """
    Parse a given condition string into a list
    Each item is a list representing separate AND conditions (all must be met)
    Each item list represents a set of OR conditions (at least one must be met)
    The item lists may contain:
        - A string, which must be a substring of one of the student's courses
        - A tuple of form (int, [str]), the student must have at least int amount of
          courses containing any of the strings in the list
    """
    # Remove the leading "Prereqs:" or similar from string
    if ':' in conditions:
        conditions = conditions[conditions.index(':') + 1:]

    # Split
    conditions = custom_split(conditions)

    # Assemble as described in docstring
    prereqs = []
    curr_and = []
    for cond in conditions:
        if cond == 'AND':
            prereqs.append(curr_and.copy())
            curr_and = []
        elif is_course_code(cond):
            curr_and.append(cond)
        elif "OR" in cond or "AND" in cond:
            curr_and.append(parse_prereqs(cond))
        elif "UNITS" in cond:
            cond_split = cond.split()
            uoc_required = int(cond_split[cond_split.index("UNITS") - 1])
            uoc_conditions = []
            if "IN" in cond:
                if "LEVEL" in cond:
                    level_idx = cond_split.index("LEVEL")
                    uoc_conditions.append(
                        cond_split[level_idx + 2] + cond_split[level_idx + 1])
                else:
                    for course in cond_split[cond_split.index("IN") + 1:]:
                        uoc_conditions.append(course.strip("( ).,"))
            else:
                uoc_conditions.append("")
            curr_and.append((uoc_required // 6, uoc_conditions))
    if curr_and != []:
        prereqs.append(curr_and)

    return prereqs


def custom_split(string):
    '''
    Splits an uppercase string into:
        course codes, "AND", "OR", items contained in brackets, uoc requirements
    '''
    simple = string.split()
    result = []
    curr_start = 0
    curr_end = 0
    while curr_end <= len(simple):
        curr = ' '.join(simple[curr_start:curr_end]).strip()
        if "UNITS" in curr:
            # If this is a uoc requirement, loop until its end
            while curr_end < len(simple) and (simple[curr_end] not in ["OR", "AND"]):
                curr_end += 1
            result.append(' '.join(simple[curr_start:curr_end]).strip())
            curr_start = curr_end
        elif '(' in curr:
            # If this an item in brackets, loop to find its closing bracket
            while curr_end <= len(simple) and not is_closed(curr):
                curr_end += 1
                curr = ' '.join(simple[curr_start:curr_end]).strip()
            result.append(curr[1:-1])
            curr_start = curr_end
        elif curr == "OR" or curr == "AND" or is_course_code(curr):
            # These are separate items
            result.append(curr)
            curr_start = curr_end

        curr_end += 1

    # Remove "OR"s as they are unnecessary
    while True:
        try:
            result.remove("OR")
        except ValueError:
            break

    return result


def is_closed(string):
    '''
    Given a string containing at least one bracket, return whether or not all brackets are closed
    '''
    return string.count('(') == string.count(')')


def is_course_code(s):
    '''
    Given a string, return whether or not it is a course code
    A course code is either 4 letters followed by 4 numbers, or just 4 numbers
    '''
    return (len(s) == 8 and s[0:4].isalpha() and s[4:8].isnumeric()) or \
           (len(s) == 4 and s.isnumeric())


def meets_prereq_list(courses_list, prereqs):
    '''
    Given a list of prereqs, return whether or not the given course list
    satisfies ALL prereqs
    '''
    for prereq in prereqs:
        if not meets_prereq(courses_list, prereq):
            return False
    return True


def meets_prereq(courses_list, prereq):
    '''
    Return if the given courses list satisfies the given prereq
    '''
    for item in prereq:
        if isinstance(item, str):
            if any(item in course for course in courses_list):
                return True
        elif isinstance(item, tuple):
            matches = 0
            for course_code in courses_list:
                if any(substring in course_code for substring in item[1]):
                    matches += 1
            if matches >= item[0]:
                return True
        elif isinstance(item, list):
            if meets_prereq_list(courses_list, item):
                return True

    return False


def is_unlocked(courses_list, target_course):
    """Given a list of course codes a student has taken, return true if the target_course
    can be unlocked by them.

    You do not have to do any error checking on the inputs and can assume that
    the target_course always exists inside conditions.json

    You can assume all courses are worth 6 units of credit
    """

    prereqs = parse_prereqs(CONDITIONS[target_course].upper())
    return meets_prereq_list(courses_list, prereqs)



if __name__ == '__main__':
    print(is_unlocked(["MATH1081", "COMP1511"], "COMP9302"))
