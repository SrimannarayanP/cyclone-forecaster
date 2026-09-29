# gen_advisories.py


from dotenv import load_dotenv

import json, os, requests, time


def generate_early_warnings(assets_path, output_path):
    load_dotenv()

    print(f"Loading vulnerable assets from {assets_path}...")

    if not os.path.exists(assets_path):
        raise FileNotFoundError("at_risk_assets.json missing. Run vulnerability_scorer.py 1st.")

    with open(assets_path, 'r') as f:
        assets = json.load(f)

    if not assets:
        print("No assets at risk. Skipping advisory gen.")

        return

    crit_assets = assets[:5] # Slice the top 5 most crit assets to avoid token limits & keep the demo focused.

    api_key = os.environ.get('GEMINI_API_KEY')

    if not api_key:
        raise ValueError("GEMINI_API_KEY env var is missing.")

    valid_model = 'models/gemini-3.8-flash'

    print(f"Using explicitly recommended model: {valid_model}")

    prompt = f"""
        You are an emergency mgmt AI for the coastal district of Puri, Odisha. A severe cyclone is approaching. Our parametric wind-field & DEM-based flood routing
        models have ID'd the following crit infra assets at highest risk of storm surge & inland flooding:

        {json.dumps(crit_assets, indent = 2)}

        Gen an actionable early-warning advisory for municipal authorities. You must output STRICTLY in the following JSON schema. Do not include md formatting or
        conversational text.

        {{
            "ward_id": "Puri_Coastal_Zone",
            "advisory_text_en": "Plain lang English action plan (e.g., evac hospitals, reroute power grid)...",
            "advisory_text_od": "Accurate Odia translation of the English text...",
            "severity_level": "CRITICAL"
        }}
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/{valid_model}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'temperature': 0.2}}

    print("Executing raw REST call to Gemini API...")

    max_retries = 5

    for attempt in range(max_retries):
        res = requests.post(url, headers = headers, json = payload)

        if res.status_code == 200:
            data = res.json()

            try:
                raw_text = data['candidates'][0]['content']['parts'][0]['text']
                raw_text = raw_text.strip().removeprefix('```json').removesuffix('```').strip()
                advisory_json = json.loads(raw_text)

                os.makedirs(os.path.dirname(output_path), exist_ok = True)

                with open(output_path, 'w', encoding = 'utf-8') as f:
                    json.dump([advisory_json], f, ensure_ascii = False, indent = 4)

                print(f"Advisory successfully gen'd & written to {output_path}")

                return
            except Exception as e:
                print(f"Failed to parse res: {e}")

                return
        elif res.status_code == 503:
            wait_time = 2**attempt

            print(f"API busy (503). Retrying in {wait_time} secs (Attempt {attempt + 1}/{max_retries})...")

            time.sleep(wait_time)
        else:
            print(f"REST API Err: {res.text}")

            return

    print("API completely unresponsive. Writing mock fallback data to unblock frontend dev.")

    mock_data = [{
        "ward_id": "Puri_Coastal_Zone",
        "advisory_text_en": "Evacuate low-lying hospitals immediately. Reroute power grids away from surge zones.",
        "advisory_text_od": "ତୁରନ୍ତ ତଳିଆ ଡାକ୍ତରଖାନାଗୁଡ଼ିକୁ ଖାଲି କରନ୍ତୁ। ବିଦ୍ୟୁତ୍ ଗ୍ରୀଡ୍‌କୁ ସର୍ଜ ଜୋନ୍‌ରୁ ଅନ୍ୟତ୍ର ସ୍ଥାନାନ୍ତର କରନ୍ତୁ।",
        "severity_level": "CRITICAL"
    }]

    os.makedirs(os.path.dirname(output_path), exist_ok = True)

    with open(output_path, 'w', encoding = 'utf-8') as f:
        json.dump(mock_data, f, ensure_ascii = False, indent = 4)


generate_early_warnings('outputs/at_risk_assets.json', 'outputs/advisories.json')