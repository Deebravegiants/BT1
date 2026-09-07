# [H] Open WebUI vulnerable to Stored XSS via iFrame in citations model

## Summary
Severity: High
Advisory: GHSA-xc8p-9rr6-97r2
CVE: CVE-2026-26192
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-xc8p-9rr6-97r2
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.7.0

## Details
### Summary
Manually modifying chat history allows setting the `html` property within document metadata. This causes the frontend to enter a code path that treats document contents as HTML, and render them in an iFrame when the citation is previewed. This allows stored XSS via a weaponised document payload in a chat. The payload also executes when the citation is viewed on a shared chat.

### Details
The vulnerability stems from how iFrame are implemented here:
https://github.com/open-webui/open-webui/blob/6f1486ffd0cb288d0e21f41845361924e0d742b3/src/lib/components/chat/Messages/Citations/CitationModal.svelte#L163-L170
The `html` attribute can be controlled by a user who manually edits the chat history. Since `allow-scripts` and `allow-same-origin` are harcoded here the sandboxing offers essentially no protection.

### PoC
Create an arbitrary chat with a file upload attached:
<img width="2462" height="1148" alt="image" src="https://github.com/user-attachments/assets/fad83c74-036d-41b8-bc44-87bf2a538b21" />
Edit the response
<img width="768" height="206" alt="image" src="https://github.com/user-attachments/assets/41a7342a-cc41-433e-8820-0bc6ed08ddd7" />
<img width="2142" height="796" alt="image" src="https://github.com/user-attachments/assets/fb731111-e082-4172-80d1-34cff6b2a511" />
Before saving, configure the browser to use an HTTP proxy tool (Burp/Caido/ZAP) and intercept the save request. Find the object within the `history` and then `messages` objects (not the `messages` array) that contains the document source.
<img width="2122" height="1388" alt="image" src="https://github.com/user-attachments/assets/1b4fbced-a6de-414d-b063-9cae44e3f449" />
Add `html: true` to metadata, update the document to an XSS payload, and forward the request.
<img width="2240" height="1358" alt="image" src="https://github.com/user-attachments/assets/fd27971b-f707-458f-a14d-254f9f3ad1fa" />
Observe the payload is rendered in the iFrame and the javascript executes.
<img width="2698" height="1696" alt="image" src="https://github.com/user-attachments/assets/b4e31cb4-d4cc-41a9-be42-802e9b1a798d" />
The payload also executes when viewed from a shared version of the chat.
<img width="2742" height="1258" alt="image" src="https://github.com/user-attachments/assets/92ee501d-8f14-4c32-8f3c-f4d3ca304ee5" />


### Impact
Any user can create a weaponised chat that can be shared and subsequently used to target other users.

Low privilege users are at risk of having their session taken over by a payload that reads their token from local storage and exfiltrates it to an attacker controlled server.

Admins are at risk of exposing the server to RCE via same chain described in https://github.com/advisories/GHSA-w7xj-8fx7-wfch.

### Caveats
The victim must expand the sources and click the document containing the payload to trigger this issue.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-xc8p-9rr6-97r2
- https://nvd.nist.gov/vuln/detail/CVE-2026-26192
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/blob/6f1486ffd0cb288d0e21f41845361924e0d742b3/src/lib/components/chat/Messages/Citations/CitationModal.svelte#L163-L170
