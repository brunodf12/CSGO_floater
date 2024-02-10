import requests 
import json 

class SkinFloater:
    def __init__(self) -> None:
        pass 
    
    # Just create a new filename for the skin stats
    @staticmethod
    def __filename__(weapon:str, skin:str, grade:str, ext:str="json") -> str:
        weapon = weapon.title().replace(" ", "")
        skin = skin.title().replace(" ", "")
        grade = grade.title().replace(" ", "")

        return f"{weapon}-{skin}-{grade}.{ext}"

    # Formats the skins response to an iterable json object
    # (seriously, how can a json response be so BAD?)
    @staticmethod
    def __skin_to_json__(response) -> object:
        data = response.replace('}]}},', "}]}}} \nsepara{").split('\n')
        data = ''.join([x for x in data if "separa" in x])
        data = data.replace('separa', " ")
        
        # Splits the json and saves on the json list
        delimiter = '}]}}}'
        data = [x + delimiter + "," for x in data.split(delimiter) if x]
        data.pop() # Pops the last item, for it is empty

        # Formats the string to be passed to the json library
        json_string = "{\"data\":[" # Will create a list with every skin in the response
        for item in data:
            json_string += item 

        json_string = json_string.rsplit(',', 1)[0] # Remove the last ","
        json_string += "]}" # Trailling array delimiter

        return json.loads(json_string)
    
    # Return all weapon ids from the skin json
    @staticmethod
    def __parse_weapon_ids__(float_search) -> list:
        weapon_ids = []
        # Iterate through the json
        for item in float_search["data"]:  
            key = list(item.keys())[0] # Get the first (and only) key of the data attribute
            
            # Scrap all the information from the skin
            link = item[key]["asset"]["market_actions"][0]["link"]
            assetid = item[key]["asset"]['id']
            listingid = item[key]["listingid"]

            # Replace all the information in the id link
            weapon_ids.append(link.replace("\\", "").replace(f"%listingid%", listingid).replace(f"%assetid%", assetid))

        return weapon_ids
    
    # Fetches the skin data from steam's marketplace
    @staticmethod
    def fetch_skin_data(steam_link) -> object:
        # Makes the get request and returns the json 
        response = requests.get(steam_link)
        float_search = SkinFloater.__skin_to_json__(str(response.content))

        return float_search

    
    # Fetches skin float data and saves as a Json if save == True
    @staticmethod
    def fetch_float_data(float_search, save=False, path=None) -> list:
        # Get the skin json and parse the weapon ids
        weapon_ids = SkinFloater.__parse_weapon_ids__(float_search)

        float_ids = []
        for wid in weapon_ids:
            # Makes the request 
            response = requests.get(f"https://api.csgofloat.com/?url={wid}")
            data = response.json()['iteminfo']
            
            # Append the skin information to a dict and then to a list
            info = { "url": wid, "float": float(data['floatvalue']) }
            float_ids.append(info)

            # Creates a filepath with the items information
            if not path:
                path = SkinFloater.__filename__(data['weapon_type'], data['item_name'], data['rarity_name'])

        # Sorts the dicts by float
        float_ids = sorted(float_ids, key=lambda d: d['float']) 

        # Saves the weapon in a json file
        if save:
            with open(path, "w", encoding='utf-8') as f:
                json.dump(float_ids, f)
            
        return float_ids


# =====================
#   **MAIN PROGRAM**
# =====================

if __name__ == "__main__":
    # Reads the txt with all the skins to test
    txt_path = "skins.txt"
    with open(txt_path, 'r', encoding='utf-8') as f:
        skins = [line.rstrip('\n').strip() for line in f]
    
    # Iterate and get all the skins
    floater = SkinFloater()
    for skin in skins:
        float_search = floater.fetch_skin_data(skin)
        floats = floater.fetch_float_data(float_search, save=True) # Save in a json
        print(skin, ":")
        print(floats)