### welcome_assignment_answers
### Input - All eight questions given in the assignment.
### Output - The right answer for the specific question.

def welcome_assignment_answers(question):
   # The student doesn't have to follow the skeleton for this assignment.
   # Another way to implement it is using "case" statements similar to C.
   if question == "Are encoding and encryption the same? - Yes/No":
       answer = "No"
       return (answer)
   elif question == "Is it possible to decrypt a message without a key? - Yes/No":
       answer = "Yes"
   return (answer)


# Complete all the questions.


if __name__ == "__main__":
   # use this space to debug and verify that the program works
   debug_question = "Are encoding and encryption the same? - Yes/No"
   print(welcome_assignment_answers(debug_question))