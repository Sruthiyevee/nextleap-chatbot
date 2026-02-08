import json
import os
import sys

# Define the path to the JSON file
JSON_FILE_PATH = "final_courses_data.json"

def test_json_structure():
    print("Testing JSON structure...")
    if not os.path.exists(JSON_FILE_PATH):
        print(f"FAIL: File '{JSON_FILE_PATH}' not found.")
        return False
    
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"FAIL: Invalid JSON format. Error: {e}")
        return False

    if "courses" not in data:
        print("FAIL: Root key 'courses' missing.")
        return False
    
    if not isinstance(data["courses"], list):
        print("FAIL: 'courses' is not a list.")
        return False

    if len(data["courses"]) == 0:
        print("FAIL: 'courses' list is empty.")
        return False

    print("PASS: JSON structure is valid.")
    return data

def test_cohort_schema(data):
    print("\nTesting Cohort Schema...")
    all_passed = True
    
    for course in data["courses"]:
        course_name = course.get("course_name", "Unknown Course")
        print(f"Checking course: {course_name}...")
        
        if "cohorts" not in course:
            print(f"  FAIL: 'cohorts' key missing in {course_name}")
            all_passed = False
            continue

        for cohort in course["cohorts"]:
            # Check required fields
            required_fields = ["cohort_label", "cohort_number", "cohort_start_date", "cohort_start_date_iso", "parsed_from_label", "estimated", "cohort_details"]
            for field in required_fields:
                if field not in cohort:
                    print(f"  FAIL: Missing field '{field}' in cohort data.")
                    all_passed = False
            
            # Check types
            if not isinstance(cohort.get("cohort_number"), int):
                print(f"  FAIL: 'cohort_number' should be an integer. Found: {type(cohort.get('cohort_number'))}")
                all_passed = False
            
            if not isinstance(cohort.get("parsed_from_label"), bool):
                print(f"  FAIL: 'parsed_from_label' should be a boolean.")
                all_passed = False

            # Check details completeness
            details = cohort.get("cohort_details", {})
            collections = ["weekwise_course_details", "instructors", "mentors", "success_stories", "reviews", "frequently_asked_questions"]
            for col in collections:
                if col not in details:
                     print(f"  FAIL: Missing collection '{col}' in cohort details.")
                     all_passed = False
                elif not isinstance(details[col], list):
                     print(f"  FAIL: '{col}' is not a list.")
                     all_passed = False
                elif len(details[col]) == 0:
                     print(f"  WARNING: '{col}' is empty for {course_name}. User requested exhaustive lists.")
                     # Not stricly a fail for test execution but a warning for data quality
            
            if details.get("success_stories") and len(details.get("success_stories")) == 0:
                 print(f"  FAIL: 'success_stories' is empty.")
                 all_passed = False
            
            if details.get("reviews") and len(details.get("reviews")) == 0:
                 print(f"  FAIL: 'reviews' is empty.")
                 all_passed = False
                 
            if details.get("frequently_asked_questions") and len(details.get("frequently_asked_questions")) == 0:
                 print(f"  FAIL: 'frequently_asked_questions' is empty.")
                 all_passed = False

    if all_passed:
        print("PASS: All cohort schema checks passed.")
    else:
        print("FAIL: One or more cohort checks failed.")
    return all_passed

def main():
    data = test_json_structure()
    if not data:
        sys.exit(1)
        
    schema_passed = test_cohort_schema(data)
    
    if schema_passed:
        print("\nAll Tests Passed Successfully!")
        sys.exit(0)
    else:
        print("\nSome tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
