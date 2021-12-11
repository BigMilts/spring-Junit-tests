'''
This file is part of an ICSE'18 submission that is currently under review.
For more information visit: https://github.com/icse18-FAST/FAST.

This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Geeral Public License
along with this source.  If not, see <http://www.gnu.org/licenses/>.
'''

import glob
import os

import fast

usage = """USAGE: python script/prioritize.script <dataset> <entity> <algorithm> <repetitions>
OPTIONS:
  <dataset>: test suite to prioritize.
    options: flex_v3, grep_v3, gzip_v1, make_v1, sed_v6, closure_v0, lang_v0, math_v0, chart_v0, time_v0
  <entity>: BB or WB (function, branch, line) prioritization.
    options: bbox, function, branch, line
  <algorithm>: algorithm used for prioritization.
    options: FAST-pw, FAST-one, FAST-log, FAST-sqrt, FAST-all, STR, I-TSD, ART-D, ART-F, GT, GA, GA-S
  <repetitions>: number of prioritization to compute.
    options: positive integer value, e.g. 50
NOTE:
  STR, I-TSD are BB prioritization only.
  ART-D, ART-F, GT, GA, GA-S are WB prioritization only."""


def bbox_prioritization(name, k, r, b, repeats, test_cases1):
    java_flag = True
    if name == "FAST-pw":
        for run in range(repeats):
            if java_flag:
                prioritization = fast.fast_pw(
                    test_cases1, r, b, bbox=True, k=k)
            return prioritization


# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Getting Test cases from java files
def get_all_java_test_files():
    """
     Gets all java test path in the repository
    """
    files = []
    files += glob.glob('**/*Test*.java', recursive=True)
    files += glob.glob('**/*__*Test*.java', recursive=True)
    return files


def compact_files(tests_directories):
    test_suites = []
    for testSuite in tests_directories:
        test_suites.append(minify_test_class(testSuite))
    return test_suites


def minify_test_class(path: str):
    file = open(path, "r")
    lines = file.readlines()
    compressed_file = ""
    for line in lines:
        compressed_file += line.replace("\n", "").strip()
    return compressed_file


def get_test_class_number(tests_directories):
    classes = {}
    for number in range(len(tests_directories)):
        classes[number + 1] = tests_directories[number]
    return classes


def write_results(results):
    directory = "../output"
    if not os.path.exists(directory):
        os.makedirs(directory)
    string_result = ''
    for result in results:
        string_result += result + "\n"
    print(string_result)


if __name__ == "__main__":
    files_paths = get_all_java_test_files()
    test_classes_order = get_test_class_number(files_paths)
    processed_test_cases = compact_files(files_paths)

    # Fast configurations
    entity = "bbox"
    algname = "FAST-pw"
    repeats = 1

    entities = {"bbox", "function", "branch", "line"}

    # FAST parameters
    k, r, b = 5, 1, 10

    priorizated_tests = bbox_prioritization(
        algname, k, r, b, repeats, processed_test_cases)

    tests_post_priorization = []
    if priorizated_tests is not None:
        for priorizated_test in priorizated_tests:
            tests_post_priorization.append(test_classes_order[priorizated_test])
        write_results(tests_post_priorization)