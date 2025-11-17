
'''Q1''''''
'Find the missing number
'==================================================================''''''''
''''''''1. Write a function that gets a list of numbers like this one:
[8, 4, 10, 2, 3, 5, 1, 9, 6]
The function will find the missing number in the sequence from 1 to 10, and return it.''''''

Example Usage:
nums1 = [8, 4, 10, 2, 3, 5, 1, 9, 6]
print(find_missing_number(nums1))  # Output: 7'''''

'======================================================================='

'''def find_missing_number(nums1):
    missing_numbers = []
    nums1 = [8, 4, 10, 2, 3, 5, 1, 9, 6]
    for num in nums1:
        if num not in missing_numbers:
            missing_numbers.append(num)
            
print(find_missing_number(nums1))''

============================================================================

Q2'''

''''Sum of Digits in a String

Create a function sum_of_digits(text) that returns the sum of all digits found in the given string. 
Non-digit characters should be ignored

# Example usage:
input_text = "abc123xyz45"
# Expected digits: 1, 2, 3, 4, 5 => total = 15
print(sum_of_digits(input_text))  # Output: 15'''''

def sum_of_digits(text):
    input_text = "abc123xyz45"
    digits = []
    for char in text:
        digits.append(int(char))

    return sum(digits)
input_text = "abc123xyz45"

print(sum_of_digits(input_text))