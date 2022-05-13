import os
import sys
import string
import fnmatch
from collections import Counter
import argparse
import random

# Dictionary from https://phillipmfeldman.org/English/spelling%20dictionaries.html


def filter_words(words_list, must_contain):
    filtered_list = words_list
    for letter in must_contain:
        filtered_list = fnmatch.filter(filtered_list, '*' + letter + '*')
    return filtered_list

def filter_out_words(words_list, must_not_contain):
    filtered_list = words_list
    exclude_filtered_list = []
    for letter in must_not_contain:
        exclude_filtered_list = fnmatch.filter(filtered_list, '*' + letter + '*')
        filtered_list = [x for x in filtered_list if x not in exclude_filtered_list]
    return filtered_list

def get_common_letters(words_list):
    return Counter("".join(words_list)).most_common()

def guess_next_word(words_list):
    common_letter_tuples = get_common_letters(words_list)
    filtered_list = words_list
    count = 0
    last_word_list = filtered_list
    for cl in common_letter_tuples:
        letter = cl[0][0]
        filtered_list = filter_words(filtered_list, str(letter))
        count = len(filtered_list)
        if verbose : print("Common letter : ", letter, " : found ", count) 
        if count == 1:
            return filtered_list
        elif count == 0:
            return last_word_list
        last_word_list = filtered_list
    return filtered_list

def score_guess(target_word : str, guess : str):
    guess_char_list = [c for c in guess]
    score_char_list = []
    for ii, letter in enumerate(guess_char_list):
        if target_word[ii] == letter:
            score_char_list.append('c')
        elif letter in target_word:
            score_char_list.append('m')
        else:
            score_char_list.append('x')
    return score_char_list

def validate_guess(guess, words_set, filtered_list, word_length, hint):
    if (guess == "h") : 
        print("Hint :", hint)
        return False
        
    if (guess == "a") : 
        print("All matching :", filtered_list)
        return False

    if len(guess) != word_length:
        return False

    if guess not in words_set:
        return False
    return True

def filter_word_list(guess, score_char_list, answer_char_list, must_contain, must_not_contain, remaining_letter_list, words_set):
    guess_char_list = [c for c in guess]
    incorrectly_placed_letters = []

    for ii, letter in enumerate(score_char_list):
        if letter == 'c':
            if guess_char_list[ii] not in must_contain:
                must_contain.append(guess_char_list[ii])
            answer_char_list[ii] = guess_char_list[ii]
        elif letter == 'm':
            if guess_char_list[ii] not in must_contain:
                must_contain.append(guess_char_list[ii])
            incorrect_letter = no_match_answer.copy()
            incorrect_letter[ii] = guess_char_list[ii]
            incorrectly_placed_letters.append(incorrect_letter)
        else :
            if guess_char_list[ii] not in (must_not_contain and must_contain):
                must_not_contain.append(guess_char_list[ii])
            # if its a double letter that is wrong (and first instance is already good), lets ensure we remove all instances of it
            if guess_char_list[ii] in must_contain: 
                incorrect_letter = no_match_answer.copy()
                incorrect_letter[ii] = guess_char_list[ii]
                incorrectly_placed_letters.append(incorrect_letter)
            

    remaining_letter_list = [x for x in remaining_letter_list if x not in must_contain]
    remaining_letter_list = [x for x in remaining_letter_list if x not in must_not_contain]

    print("Correct letters so far : ", "".join(answer_char_list))
    print("Must contain : ", must_contain)
    print("Must not contain : ", must_not_contain)
    print("Remaining letter : ", "".join(remaining_letter_list))

    filtered_list = fnmatch.filter(words_set, "".join(answer_char_list))

    if verbose: print(len(filtered_list), " matches found")

    filtered_list = filter_words(filtered_list, must_contain)
    if verbose: print(len(filtered_list), " filtered with included letters")
    
    filtered_list = filter_out_words(filtered_list, must_not_contain)
    if verbose: print(len(filtered_list), " filtered with excluded letters")

    for incorrectly_placed in incorrectly_placed_letters:
        if verbose : print(incorrectly_placed)
        incorrect_letter_list = fnmatch.filter(filtered_list, "".join(incorrectly_placed))
        filtered_list = [x for x in filtered_list if x not in incorrect_letter_list]
    if verbose: print(len(filtered_list), " filtered with correct letters in the wrong place") 

    return filtered_list

#################################################
#
# Main
#
#################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(allow_abbrev=False, description="PyWordle Game")
    parser.add_argument('--helper', default=False, action='store_true', help='Help to solve an external Wordle')
    parser.add_argument('--verbose', default=False, action='store_true', help='Verbose output')
    parser.add_argument('--answer', default=None, help='Provide the Answer')
    parser.add_argument('--hint', default=None, action='store_true', help='Show hints')
    args = parser.parse_args()

    dictionary_file = os.path.join('data', 'large.txt')
    word_length = 5

    # Load the dictionary
    with open(dictionary_file, 'r') as FILE:
        words_list = [ word.rstrip() for word in FILE if len(word.rstrip()) == word_length]
    full_words_set = set(words_list)
    words_set = full_words_set.copy()

    # A few defaults
    answer = ['?' for x in range(word_length)]
    must_contain = []
    must_not_contain = []
    remaining_letters = [x for x in string.ascii_lowercase]

    verbose = args.verbose
    no_match_answer = ['?' for x in range(word_length)]

    if not args.helper:
        target_word = random.choice(words_list)
        if args.answer != None : target_word = args.answer

    for turn in range(1, 7):
        print("="*20)
        print("Turn ", turn)
        print("="*20)
        hint = guess_next_word(words_set)
        if args.hint or args.helper:
            print("Hint : ", hint)
        print("Answer so far : ", answer)
        print("Enter your guess :")

        guess = input().lower()
#        if not args.helper:
        while(not validate_guess(guess, full_words_set, words_set, word_length, hint)):
            print("Invalid guess")
            guess = input().lower()
        print(guess)

        if args.helper:
            print("Enter your results [c:correct, m:wrong place, x:Wrong] :")
            score = input().lower()
            while (len(score) != word_length):
                print("Wrong length. Word needs to be of length ", word_length)
                score = input().lower()
            score_char_list = [c for c in score]
        else:
            score_char_list = score_guess(target_word, guess)
            print("Your results [c:correct, m:wrong place, x:Wrong] :")
            print(score_char_list)

        if score_char_list == ['c' for x in range(word_length)]:
            print("You Won in ", turn)
            if not args.helper:
                print("The correct answer is", target_word)
            exit(0)

        filtered_list = filter_word_list(guess, score_char_list, answer, must_contain, must_not_contain, remaining_letters, words_set)

        if args.hint or args.helper: print(len(filtered_list), " words available") 

        if verbose : print(filtered_list)

        words_set = set(filtered_list)

    if args.helper:
        print("The remaining words list was :", filtered_list)
    else:
        print("The answer was : ", target_word)


