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
import sys

# NOTE: DO NOT EDIT conditions.json
with open("./conditions.json") as f:
    CONDITIONS = json.load(f)
    f.close()

def parse_prereqs(course: str):
    """
    Given a course code, return a list with a set of conditions that must each be met
    These conditions are either:
        A list of strings, the student must have completed a course in this string
        A list of lists of strings, similar to above
        A tuple with an int and a list of strings, there must be at least int amount of strings containing one of the strings in the list
    """
    prereqs = []
    # Get the condition and string and convert to uppercase
    with open("conditions.json") as FILE:
        conditions = json.load(FILE)[course].upper()
    
    # Remove the leading "Prereqs:" from string
    if ':' in conditions:
        conditions = conditions[conditions.index(':') + 1:]

    # First split by ANDs
    and_conditions = [s.strip("( ).,") for s in conditions.split("AND")]

    for ac in and_conditions:
        current_and = []
        # Now split by OR and add to a list in the list
        or_conditions = [s.strip("( ).,") for s in ac.split("OR")]
        for oc in or_conditions:
            if is_course_code(oc):
                current_and.append(oc)
            elif "UNITS" in oc:
                oc_split = oc.split()
                uoc_required = int(oc_split[oc_split.index("UNITS") - 1])
                uoc_conditions = []
                if "IN" in oc:
                    if "LEVEL" in oc:
                        level_idx = oc_split.index("LEVEL")
                        uoc_conditions.append(oc_split[level_idx + 2] + oc_split[level_idx + 1])
                    else:
                        for course in oc_split[oc_split.index("IN") + 1:]:
                            uoc_conditions.append(course.strip("( ).,"))
                else:
                    uoc_conditions.append("")

                current_and.append((uoc_required // 6, uoc_conditions))

        if current_and != []:
            prereqs.append(current_and)

    return prereqs

def is_course_code(s: str):
    '''
    Given a string, return whether or not it is a course code
    '''
    return (len(s) == 8 and s[0:4].isupper() and s[4:8].isnumeric()) or \
           (len(s) == 4 and s.isnumeric())

def is_unlocked(courses_list, target_course):
    """Given a list of course codes a student has taken, return true if the target_course 
    can be unlocked by them.
    
    You do not have to do any error checking on the inputs and can assume that
    the target_course always exists inside conditions.json

    You can assume all courses are worth 6 units of credit
    """
    prereqs = parse_prereqs(target_course)

    print(prereqs)

    for pr in prereqs:
        for item in pr:
            if isinstance(item, str):
                if not any(x in y for x in pr for y in courses_list):
                    return False
            # if isinstance(item, list):
            #     for l in pr:
            #         if not any(x in y for x in l for y in courses_list):
            #             return False
            if isinstance(item, tuple):
                matches = 0
                for substring in item[1]:
                    for course_code in courses_list:
                        if substring in course_code:
                            matches += 1
                if matches < item[0]:
                    return False

    return True


if __name__ == '__main__':
    print(parse_prereqs(sys.argv[1]))
    # print(is_unlocked(["COMP1521", "COMP1531", "COMP1511", "COMP2521", "COMP2511", "COMP2000"], "COMP3901"))

    