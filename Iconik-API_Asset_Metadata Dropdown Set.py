import requests, sys, json, subprocess, os, argparse
import xml.etree.ElementTree as ET

def similarity_check(xml_data, user_option):
    xml_root = ET.fromstring(xml_data)
    matched_scores = []

    for elem in xml_root.findall(".//word"):
        elem_match = elem.find("match")
        elem_word = elem.get("name")
        elem_score = elem.find("score")

        # Condition elem_match and elem_score
        elem_match_value = elem_match.text.strip().lower() if elem_match is not None or "" else "false" # type: ignore
        elem_score_value = float(elem_score.text) if elem_score is not None or "" else 0.0 # type: ignore
        elem_name_value = elem_word.strip().lower() if elem_word is not None or "" else "" # type: ignore

        if elem_match_value == "true" and elem_score_value >= 60.0:
            matched_scores.append((elem_match_value, elem_score_value, elem_name_value))

    if matched_scores.__len__() > 0:
        matched_scores.sort(key=lambda x: x[1], reverse=True)

        top_match = matched_scores[0]
        top_match_score = top_match[1]
        top_match_name = top_match[2]

        for option in dropdown_field_options:
            if option["label"].lower() == top_match_name:
                message = ""
                if top_match_score < 100.0:
                    message = f'"{user_option}" is misspelled. Is it meant to be "{option["label"]}"?'
                return [True, option, message]
                
    return [False, elem_word, ""]

def create_html_message(message_list):
    if len(message_list) == 0:
        return ""
    message = "See below list tags that are misspelled or not matching any dropdown option selections:<br><ul>"
    for msg in message_list:
        message += f"<li>{msg}</li>"
    message += "</ul>"

    list_total = len(DROPDOWN_VALUES)
    blank_count = list_total - sum(1 for value in DROPDOWN_VALUES if value is None or (isinstance(value, str) and value.strip() == ""))
    
    if blank_count > 0:
        message += f'<br><br>Below is a list of tag(s) that could not be matched to any dropdown option. Please review and fix manually:<br><ul>'
        for values in DROPDOWN_VALUES:
            if values is None or (isinstance(values, str) and values.strip() == ""):
                message += f"<li>{values}</li>"
        message += "</ul>"

    message += f'<br><br><p style="font-size: 12px; color: gray; font-family: Cambria,Times New Roman,Calibri,Segoe UI,Sans-Serif;">This message was automatically generated.</p>'
    return message


parser = argparse.ArgumentParser(description="Updates dropdown metadata field values for an asset")
parser.add_argument("-app-id", "--app-id", "-a", dest="APP_ID", type=str, required=True, help="Iconik App ID")
parser.add_argument("-auth-token", "--auth-token", "-t", dest="AUTH_TOKEN", type=str, required=True, help="Iconik Auth Token")
parser.add_argument("-asset-id", "--asset-id", "-i", dest="ASSET_ID", type=str, required=True, help="Iconik Asset ID to update metadata field values for")
parser.add_argument("-dropdown-values", "--dropdown-values", "-v", dest="INPUT_DROPDOWN_VALUES", type=str, required=True, help="Comma-separated list of dropdown option values to update the metadata field with")
parser.add_argument("-metadata-field-name", "--metadata-field-name", "-m", dest="META_DATA_FIELD_NAME", type=str, required=True, help="Metadata field name to update")

args = parser.parse_args()

if not args.APP_ID or not args.AUTH_TOKEN or not args.ASSET_ID or not args.INPUT_DROPDOWN_VALUES or not args.META_DATA_FIELD_NAME:
    sys.exit(1)

APP_ID = args.APP_ID
AUTH_TOKEN = args.AUTH_TOKEN
ASSET_ID = args.ASSET_ID
INPUT_DROPDOWN_VALUES = args.INPUT_DROPDOWN_VALUES
META_DATA_FIELD_NAME = args.META_DATA_FIELD_NAME

headers = {
    'App-ID': APP_ID,
    'Auth-Token': AUTH_TOKEN,
    'Content-Type': 'application/json'
}

object_type = "assets"
asset_id = ASSET_ID
object_id = asset_id if object_type == "assets" else ""
base_url = "https://app.iconik.io/API"

matched_options = []

# Checks to see if INPUT_DROPDOWN_VALUES contains text (not empty)
if INPUT_DROPDOWN_VALUES is None or INPUT_DROPDOWN_VALUES.strip() == "" or len(INPUT_DROPDOWN_VALUES.strip()) == 0 or INPUT_DROPDOWN_VALUES.strip(",") == "" or len(INPUT_DROPDOWN_VALUES.strip(",")) == 0:
    print("")
    quit(0)

# Changes case to lower of all strings passed and then split by comma
DROPDOWN_VALUES_input = [value.strip() for value in INPUT_DROPDOWN_VALUES.split(",") if value.strip() != ""]
DROPDOWN_VALUES_input.sort()
DROPDOWN_VALUES = [value.lower() for value in DROPDOWN_VALUES_input]
DROPDOWN_VALUES.sort()
message_list = []

response = requests.get(f'{base_url}/metadata/v1/fields/{META_DATA_FIELD_NAME}/', headers=headers)

if response.status_code != 200:
    print(f'Error: {response.status_code}\n{response.text}')
    quit(1)

# Get all dropdown field options from JSON response
dropdown_field_options = response.json().get("options", [])

# Match input string values to dropdown options
for user_option in DROPDOWN_VALUES_input:
    sub_command = [
         sys.executable,
         os.path.join(os.path.dirname(__file__), "Word_Similar_Ratio_XML.py"),
         "-text", user_option,
         "-list", ",".join([option["label"] for option in dropdown_field_options]),
         "-test",
         "-alt"
    ]

    sub_result = subprocess.run(sub_command, capture_output=True, text=True)
    xml_output = sub_result.stdout

    is_match, option, message = similarity_check(xml_output, user_option)

    if is_match:
        matched_options.append(option)
        DROPDOWN_VALUES[DROPDOWN_VALUES.index(user_option.lower())] = "" # Remove dropdown value because it was matched
        if message != "":
            message_list.append(message)

# Convert matched_options from list to JSON string
matched_options_json = json.dumps(matched_options, indent=4)

# Construct payload data for updating metadata
payload = {
    "metadata_values": {
        META_DATA_FIELD_NAME: {
            "field_values": matched_options,
            "mode": "overwrite"
        }
    }
}

response = requests.put(f'{base_url}/metadata/v1/{object_type}/{object_id}/', headers=headers, data=json.dumps(payload))

if response.status_code != 200:
    print(f"Error: {response.status_code}\n{response.text}")
    quit(1)
else:
    return_message = create_html_message(message_list)
    #print("Success!")
    print(return_message)
    quit(0)