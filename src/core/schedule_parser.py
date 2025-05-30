import json
import re
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ScheduleEntry:
    week: str
    startTime: str
    endTime: str
    classroom: Optional[str]
    courseCode: int

def parse_time_range(time_str: str) -> tuple:
    """Parse time range like '10:30-11:45' or '13:00-13:50'"""
    time_str = time_str.strip()
    
    # Look for time pattern with colon and hyphen
    time_pattern = r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})'
    match = re.search(time_pattern, time_str)
    
    if match:
        return match.group(1), match.group(2)
    
    # If no range found, try to find single time
    single_time_pattern = r'(\d{1,2}:\d{2})'
    match = re.search(single_time_pattern, time_str)
    if match:
        single_time = match.group(1)
        return single_time, single_time
    
    return "", ""

def parse_classroom(room_str: str) -> Optional[str]:
    """Extract classroom name without parentheses"""
    if not room_str or room_str == '-':
        return None
    
    # Remove content in parentheses at the end
    match = re.search(r'^([^(]+)', room_str)
    if match:
        return match.group(1).strip()
    return room_str.strip() if room_str.strip() != '-' else None

def parse_schedule_entry(entry: str) -> List[ScheduleEntry]:
    """Parse a single schedule entry like '화 목 10:30-11:45 (진리관 11304-김기일)'"""
    if not entry.strip():
        return []
    
    # Split by newlines to handle multiple entries
    entries = entry.strip().split('\n')
    results = []
    
    for single_entry in entries:
        single_entry = single_entry.strip()
        if not single_entry:
            continue
            
        # Extract classroom info (everything in parentheses)
        classroom_match = re.search(r'\(([^)]+)\)', single_entry)
        classroom = None
        if classroom_match:
            classroom_info = classroom_match.group(1)
            # Remove professor name (after dash)
            if '-' in classroom_info:
                classroom = classroom_info.split('-')[0].strip()
            else:
                classroom = classroom_info.strip()
            
            # Remove parentheses part from the entry
            single_entry = re.sub(r'\([^)]+\)', '', single_entry).strip()
        
        # Parse the remaining part: days and time
        # Look for time pattern first
        time_pattern = r'(\d{1,2}:\d{2}(?:\s*-\s*\d{1,2}:\d{2})?)'
        time_match = re.search(time_pattern, single_entry)
        
        if not time_match:
            continue
            
        time_part = time_match.group(1)
        
        # Everything before the time is days
        before_time = single_entry[:time_match.start()].strip()
        days = before_time.split()
        
        # Parse time range
        start_time, end_time = parse_time_range(time_part)
        
        if not start_time:  # Skip if time parsing failed
            continue
        
        # Create entries for each day
        for day in days:
            if day in ['월', '화', '수', '목', '금', '토', '일']:
                results.append(ScheduleEntry(
                    week=day,
                    startTime=start_time,
                    endTime=end_time,
                    classroom=classroom,
                    courseCode=0  # Will be set later
                ))
    
    return results

def convert_json_file(input_file: str, output_file: str):
    """Convert a JSON file to the new format"""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    converted_courses = []
    
    for course in data:
        code = course.get('code', '')
        schedule_room = course.get('schedule_room', '')
        
        try:
            course_code = int(code) if code else 0
        except (ValueError, TypeError):
            course_code = 0
        
        schedule_entries = parse_schedule_entry(schedule_room)
        
        # Set course code for all entries
        for entry in schedule_entries:
            entry.courseCode = course_code
        
        # Add original course data with parsed schedules, but remove schedule_room and use courseTime
        converted_course = {
            **{k: v for k, v in course.items() if k != 'schedule_room'},  # Remove schedule_room
            'courseTime': [
                {
                    'week': entry.week,
                    'startTime': entry.startTime,
                    'endTime': entry.endTime,
                    'classroom': entry.classroom,
                    'courseCode': entry.courseCode
                }
                for entry in schedule_entries
            ]
        }
        
        converted_courses.append(converted_course)
    
    # Save converted data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_courses, f, ensure_ascii=False, indent=2)
    
    print(f"Converted {input_file} -> {output_file}")
    print(f"Total courses: {len(converted_courses)}")
    total_schedules = sum(len(course['courseTime']) for course in converted_courses)
    print(f"Total schedule entries: {total_schedules}")

def process_all_files():
    """Process all JSON files in the 2025_1 directory"""
    input_dir = "2025_1"
    output_dir = "2025_1_converted"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    
    for json_file in json_files:
        input_path = os.path.join(input_dir, json_file)
        output_path = os.path.join(output_dir, json_file)
        
        try:
            convert_json_file(input_path, output_path)
        except Exception as e:
            print(f"Error processing {json_file}: {e}")

if __name__ == "__main__":
    # Test with a specific file first
    test_file = "2025_1/2025_1학기_IT대학_소프트웨어학부_전공.json"
    if os.path.exists(test_file):
        print("Testing with software department file...")
        convert_json_file(test_file, "test_output.json")
        print("\n" + "="*50 + "\n")
    
    # Process all files
    print("Processing all files...")
    process_all_files()
    
    print("\nConversion completed!")

# === 기존 인터페이스 호환용 래퍼 ===
class ScheduleParser:
    def parse_schedule_entry(self, entry: str, course_code: int = 0):
        entries = parse_schedule_entry(entry)
        for e in entries:
            e.courseCode = course_code
        return entries

CourseTime = ScheduleEntry 