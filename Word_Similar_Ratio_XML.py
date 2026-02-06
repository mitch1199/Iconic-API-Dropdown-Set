import sys, re
from rapidfuzz import fuzz
from decimal import Decimal, ROUND_HALF_UP
from xml.etree.ElementTree import Element, SubElement, tostring

# Use RapidFuzz to get score of similarity of the txt and the sample word comparing to
def likeness(txt, sample, threshold=60.5):
    like_score = fuzz.ratio(txt, sample)
    return like_score >= threshold, like_score, sample

# Loop through an array to return True to the first item that has a True similarity score, otherwise
# returns False if no items match
def check_likeness(arr):
    return_arr = []
    for word in arr:
        #word[0] = string
        #word[1] = boolean True/False for matching similarity threshold
        #word[2] = similarity score
        if word[1] == True:
            # Return whole array item that matches
            score = Decimal(word[2]).quantize(Decimal("0"), rounding=ROUND_HALF_UP)
            x = [word[0], word[1], int(score), word[3]]
            return_arr.append(x)
        #return word[0], word[1], int(score)
    return return_arr        

if __name__ == "__main__":
    # Checking argument count

    if len(sys.argv) < 4:
        print("Usage of this script requires a text value sent as an argument and a word to match.")
        sys.exit(1)
    
    text_sample = sys.argv[1]
    match_word = sys.argv[2].split(",")
    testing = sys.argv[3].lower()
    text_alt_split = sys.argv[4] if len(sys.argv) > 4 else False

    # text_sample = "S2E3_Synopsis-Episode-Credit_v3"
    # match_word = "Synopsis,Credits,Music Sheet".split(",")
    # testing = "true"
    
    # Check if text_sample and the match_word provided are not blank
    if (len(text_sample) != 0 and len(match_word) != 0) and (text_sample.strip() != ""):
        
        # Create blank array to hold all words from text_sample
        final_arr = []
        splitText = []

        # Split text_sample into each word and add to splitText array
        splitText = [w for w in re.split(r'[_-]+', text_sample) if w]

        # Get similarity score of each word and add each array result to each item in the final_arr
        # Each array item in final_arr is an array of data
        for i in range(len(splitText)):
            for sample_word in match_word:
                result = likeness(splitText[i], sample_word)
                result_arr = [splitText[i], result[0], result[1], result[2]]

                final_arr.append(result_arr)

        # Print to console the final True/False value if there were any words that were similar to
        # the match_word
        if (testing == "true"):
            likeness_result = check_likeness(final_arr)

            # Create the XML root of 'matches'
            xml_root = Element("matches")
            for sample_word in match_word:
                xml_element = SubElement(xml_root, "word", name=sample_word)
                
            # Check if there are no files matching the word
            if not likeness_result:
                for e in xml_root.findall(f".//word"):
                    SubElement(e, "string").text = ""
                    SubElement(e, "match").text = "False"
                    SubElement(e, "score").text = "0"
                likeness_result = tostring(xml_root, encoding="unicode")
                print(likeness_result)
                sys.exit(0)

            # Add <word> elements with name attributes of match_words
            # and add child elements with likeness values
            for word in likeness_result:
                xml_match_element = xml_root.find(f".//word[@name='{word[3]}']")

                if xml_match_element is not None:
                    SubElement(xml_match_element, "string").text = str(word[0])
                    SubElement(xml_match_element, "match").text = str(word[1])
                    SubElement(xml_match_element, "score").text = str(word[2])
                
            # Find any empty <word> element and add empty child elements
            for e in xml_root.findall(f".//word"):
                if len(list(e)) == 0:
                    SubElement(e, "string").text = ""
                    SubElement(e, "match").text = "False"
                    SubElement(e, "score").text = "0"

            # Create XML format result
            likeness_result = tostring(xml_root, encoding="unicode")
            print(likeness_result)
            sys.exit(0)
        elif testing == "false":
            print(final_arr)
            sys.exit(0)
    else:
        print("Sample text or the word to match cannot be empty.")
        sys.exit(1)