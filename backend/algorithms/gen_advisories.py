# gen_advisories.py


from dotenv import load_dotenv

import json, os, requests


def generate_warnings(crit_assets):
    if not crit_assets:
        return {
            'ward_id': 'Puri_Coastal_Zone',
            'advisory_text_en': "No critical assets at immediate risk.",
            'advisory_text_od': "କୌଣସି ଜରୁରୀକାଳୀନ ସମ୍ପତ୍ତି ବିପଦରେ ନାହିଁ।",
            'severity_level': 'CLEAR'
        }

    load_dotenv()

    top_assets = crit_assets[:5]
    
    api_key = os.environ.get('GEMINI_API_KEY')
    
    valid_model = 'models/gemini-3.8-flash'

    if not api_key:

        return {
            'ward_id': 'SYSTEM_AUTH',
            'advisory_text_en': "The system is missing the API key required to generate an advisory.",
            'advisory_text_od': "ଏପିଆଇ କି (API Key) ନାହିଁ।",
            'severity_level': 'OFFLINE'
        }
    
    prompt = f"""
        You are an emergency mgmt AI for Puri, Odisha. A severe cyclone is approaching.
        Crit infra at risk:
        {json.dumps(top_assets, indent = 2)}
        
        Gen an actionable early-warning advisory. Output STRICTLY in JSON:
        {{
            "ward_id": "Puri_Coastal_Zone",
            "advisory_text_en": "Plain English action plan...",
            "advisory_text_od": "Odia translation...",
            "severity_level": "CRITICAL"
        }}
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/{valid_model}:generateContent?key={api_key}"

    try:
        res = requests.post(url, headers = {'Content-Type': 'application/json'}, json = {'contents': [{'parts': [{'text': prompt}]}]}, timeout = 8)
        
        if res.status_code == 503:

            return {
                'ward_id': 'SYSTEM_API',
                'advisory_text_en': "The AI service is currently too busy to respond. Please rely on standard evacuation protocols.",
                'advisory_text_od': "ଜେମିନି ଏପିଆଇ ବର୍ତ୍ତମାନ ବ୍ୟସ୍ତ ଅଛି (503)। ଷ୍ଟାଣ୍ଡାର୍ଡ ପ୍ରୋଟୋକଲ୍ ବ୍ୟବହାର କରନ୍ତୁ।",
                'severity_level': 'OVERLOADED'
            }

        res.raise_for_status()
        
        raw = res.json()['candidates'][0]['content']['parts'][0]['text']
    
        return json.loads(raw.strip().removeprefix('```json').removesuffix('```').strip())
    except requests.exceptions.Timeout:

        return {
            'ward_id': 'SYSTEM_NET',
            'advisory_text_en': "The AI took too long to generate a response. Please review the map data & issue warnings manually.",
            'advisory_text_od': "ପରାମର୍ଶ ପ୍ରସ୍ତୁତି ସମୟ ସୀମା ପାର ହୋଇଯାଇଛି। ମାନୁଆଲ୍ ସମୀକ୍ଷା ଆରମ୍ଭ କରନ୍ତୁ।",
            'severity_level': 'TIMEOUT'
        }
    except requests.exceptions.RequestException as e:

        return {
            'ward_id': 'SYSTEM_NET',
            'advisory_text_en': f"We lost the network connection while attempting to reach the AI service.",
            'advisory_text_od': "ନେଟୱାର୍କ ତ୍ରୁଟି।",
            'severity_level': 'OFFLINE'
        }
    except json.JSONDecodeError:

        return {
            'ward_id': 'SYSTEM_PARSE',
            'advisory_text_en': "We received an unreadable response from the AI. Manual review is required.",
            'advisory_text_od': "ଏଲଏଲଏମ୍ ତ୍ରୁଟିପୂର୍ଣ୍ଣ ତଥ୍ୟ ପ୍ରଦାନ କରିଛି। ମାନୁଆଲ୍ ଓଭରରାଇଡ୍ ଅପେକ୍ଷାରେ ଅଛି।",
            'severity_level': 'PARSE_ERROR'
        }
