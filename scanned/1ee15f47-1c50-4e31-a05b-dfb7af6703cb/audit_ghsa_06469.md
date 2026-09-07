# [M] Open WebUI has Blind Server Side Request Forgery in its Image Edit Functionality

## Summary
Severity: Medium
Advisory: GHSA-jgx9-jr5x-mvpv
CVE: CVE-2026-34225
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-jgx9-jr5x-mvpv
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0

## Details
### Summary
There is a blind server side request forgery in the functionality that allows editing an image via a prompt. The affected function will perform a GET request on the URL provided by the user. There is no restriction on the domain of the provided URL allowing the local address space to be interacted with. Since the SSRF is blind (the response cannot be read) impact is port scanning of the local network because it can be confirmed if the port is open based on if the GET request failed.

### Details
The vulnerability occurs here:
https://github.com/open-webui/open-webui/blob/2b26355002064228e9b671339f8f3fb9d1fafa73/backend/open_webui/routers/images.py#L850-L916
Line 911 shows the user provided URL passed to the function `load_url_image`. Within this function on line 883 HTTP/HTTPs URLs are trusted blindly and called asynchronously with `requests.get`. 

### PoC
The vulnerability can be reproduced with the following curl command:
```
curl -X POST http://localhost:3000/api/v1/images/edit \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"form_data":{
    "image": "<url>",
    "prompt": "poc"}
  }'
```

### Impact
Response differentials can be used to port scan the local network:
<img width="3016" height="736" alt="image" src="https://github.com/user-attachments/assets/93b4df52-b23c-4ed7-a5fa-9cbedb30091c" />
This can be automated to iterate through the entire port range to determine open ports. If the service running on an open port can be inferred the user may be able to interact with it in a meaningful way if the service offers any state changing GET request endpoints.

### Remediation
Restrict provided URLs from local address space.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-jgx9-jr5x-mvpv
- https://nvd.nist.gov/vuln/detail/CVE-2026-34225
- https://github.com/open-webui/open-webui
