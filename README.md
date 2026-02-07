# Iconic Asset Dropdown Metadata Field Updater
Update a metadata dropdown field using the Swagger API of Iconik. Input is verified by a text similarity check script for a complete match to options set in the dropdown field.

### Requirements
* ```pip install -r requirements```
* [Python 3.10+](https://www.python.org/downloads/) (older verisons may work but not tested)
* Iconik account with admin privilages
  
## Usage
### Inputs
```
-app-id, --app-id, -a                            |  Iconik Application ID
-auth-token, --auth_token, -t                    |  Iconik Authentication Token
-asset-id, --asset-id, -i                        |  Asset ID to target
-dropdown-values, --dropdown-values, -v          |  Comma-separated list of values in the Dropdown field
-metadata-field-name, --metadata-field-name, -m  |  Metadata dropdown field name
```

### Example
```python
-app-id <APP_ID> -auth-token <AUTH_TOKEN> -asset-id <ASSET_ID> -dropdown-values <VALUES> -metadata-field-name <NAME>
```

### Returns
If there are dropdown values in ```-dropdown-values``` that are not found or mispelled of values in the ```-metadata-field-name``` field, then a message is returned with __exit code 1__.

> [!NOTE]
> Return message is formatted in HTML

<details open>
<summary>Word Similarity Script</summary>

## Word Similarity script
### Usage
```
-text, --text, -t  |  String being tested
-list, --list, -l  |  Single or comma-seprated list of strings to compare against -text
-test, --test, -t  |  Leave off to print XML output to console and exit
-alt, --alt, -a    |  [Opt] Split -list by commas instead of dashes and underscores
```

### Example
```python
-text <STRING> -list <STRING> [-test -alt]
```

### Output
XML Output
```xml
<matches>
  <word name="_string_">
    <string>_string_</string>
    <match>_true/false_</match>
    <score>_score_</score>
  </word>
</matches>
```
```match``` will be ```true``` when ```score``` is greater than the set similarity percentage.

_Shown values are not actual output_
