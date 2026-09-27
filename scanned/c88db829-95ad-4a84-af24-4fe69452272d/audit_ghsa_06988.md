# [H] Open WebUI vulnerable to Stored XSS via iFrame embeds in response messages

## Summary
Severity: High
Advisory: GHSA-vjm7-m4xh-7wrc
CVE: CVE-2026-26193
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-vjm7-m4xh-7wrc
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.6.44

## Details
### Summary
Manually modifying chat history allows setting the `embeds` property on a response message, the content of which is loaded into an iFrame with a sandbox that has `allow-scripts` and `allow-same-origin` set, ignoring the "iframe Sandbox Allow Same Origin" configuration. This enables stored XSS on the affected chat. This also triggers when the chat is in the shared format. The result is a shareable link containing the payload that can be distributed to any other users on the instance.

### Details
The flaw stems from how iFrames are constructed here:
https://github.com/open-webui/open-webui/blob/6f1486ffd0cb288d0e21f41845361924e0d742b3/src/lib/components/chat/Messages/ResponseMessage.svelte#L689-L703

`messages.embeds` is a user controlled property and so can be arbitrarily set by the user to a payload of their choosing. Since `allowScripts` and `allowSameOrigin` are harcoded as true here the sandboxing offers essentially no protection.

### PoC
Create an arbitrary chat:
<img width="2468" height="1426" alt="image" src="https://github.com/user-attachments/assets/41e32f5c-3fa7-4208-a71f-85556eec6309" />
Edit the model response:
<img width="632" height="192" alt="image" src="https://github.com/user-attachments/assets/b1e79303-360f-46e3-8d6d-3309c3ec30af" />
<img width="2150" height="434" alt="image" src="https://github.com/user-attachments/assets/78f19d7f-10dc-4e91-83cc-2d4811e58496" />
Before saving, configure the browser to use an HTTP proxy tool (Burp/Caido/ZAP) and intercept the save request. Find the object within the `history` and then `messages` objects (not the `messages` array) that corresponds to the edited text.
<img width="2024" height="1528" alt="image" src="https://github.com/user-attachments/assets/953e5368-8e93-428b-b223-c695eacfe7b9" />
On this object, add an `embeds` key and list value as shown below, forward the request and refresh the page.
<img width="1904" height="1530" alt="image" src="https://github.com/user-attachments/assets/0e56be6f-5513-490e-9961-972bdfbd5d8b" />
This results in XSS via the controlled content getting rendered in the iFrame. Note the bold text is just to aid demonstration. `console.log` is used to prove JS execution because the lack of `allow-modals` on the iFrame sandbox prevents alerts. 
<img width="2752" height="1686" alt="image" src="https://github.com/user-attachments/assets/4858f7b3-4e2f-4fab-a5a5-196df26bcdce" />
The same payload triggers when the chat is shared.
<img width="2730" height="1426" alt="image" src="https://github.com/user-attachments/assets/ee88b538-9781-4276-b681-9953974b826d" />

### Impact
Any user can create a weaponised chat that can be shared and subsequently used to target other users.

Low privilege users are at risk of having their session taken over by a payload that reads their token from local storage and exfiltrates it to an attacker controlled server.

Admins are at risk of exposing the server to RCE via same chain described in GHSA-w7xj-8fx7-wfch.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-vjm7-m4xh-7wrc
- https://nvd.nist.gov/vuln/detail/CVE-2026-26193
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/blob/6f1486ffd0cb288d0e21f41845361924e0d742b3/src/lib/components/chat/Messages/ResponseMessage.svelte#L689-L703
