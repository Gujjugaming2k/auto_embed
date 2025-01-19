from flask import Flask, request, jsonify, redirect
import requests
import re

app = Flask(__name__)

def fetch_m3u8_url_from_html(url, language="Hindi"):
    try:
        # Fetch the HTML response
        response = requests.get(url)
        response.raise_for_status()

        # Extract the JavaScript object containing the `.m3u8` links
        script_pattern = re.search(r'var player = new Playerjs\((\{.*?\})\);', response.text, re.DOTALL)
        if script_pattern:
            js_object = script_pattern.group(1)

            # Extract all `.m3u8` links with their corresponding titles
            m3u8_links = re.findall(r'\{"title":\s*"(.*?)",\s*"file":\s*"(.*?)"\}', js_object)

            # Find the m3u8 URL for the specified language
            for title, file_url in m3u8_links:
                if title.lower() == language.lower():
                    return {"status": "success", "language": language, "m3u8_url": file_url}

            return {"status": "error", "message": f"No m3u8 URL found for language '{language}'."}
        else:
            return {"status": "error", "message": "Could not find player.js data in the HTML response."}
    except requests.RequestException as e:
        return {"status": "error", "message": f"An error occurred while fetching the URL: {e}"}

def modify_m3u8_url(original_url):
    # Modify the URL to append '1080' before '/index.m3u8'
    modified_url = original_url.replace('/index.m3u8', '/1080/index.m3u8')
    return modified_url

@app.route('/fetch_m3u8', methods=['GET'])
def fetch_m3u8():
    url = request.args.get('url')
    language = request.args.get('language', 'Hindi')  # Default language is Hindi

    if not url:
        return jsonify({"status": "error", "message": "URL parameter is required."}), 400

    result = fetch_m3u8_url_from_html(url, language)
    return jsonify(result)

@app.route('/redirect_to_m3u8', methods=['GET'])
def redirect_to_m3u8():
    url = request.args.get('url')
    language = request.args.get('language', 'Hindi')  # Default language is Hindi

    if not url:
        return jsonify({"status": "error", "message": "URL parameter is required."}), 400

    result = fetch_m3u8_url_from_html(url, language)
    
    if result['status'] == 'success':
        modified_url = modify_m3u8_url(result['m3u8_url'])
        return redirect(modified_url)  # Redirect to the modified m3u8 URL
    else:
        return jsonify(result)  # Return the error message as JSON

if __name__ == '__main__':
    app.run(debug=True, port=5012)
