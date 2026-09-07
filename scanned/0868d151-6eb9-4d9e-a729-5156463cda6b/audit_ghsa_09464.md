# [M] Open WebUI's Improper Authorization in Standard Channels Allows Message Updates with Read Permission

## Summary
Severity: Medium
Advisory: GHSA-jgj3-r8hr-9pjw
CVE: CVE-2026-44571
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-jgj3-r8hr-9pjw
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.8.6

## Details
## Vulnerability Description

In standard channels (i.e., channels whose `channel.type` is neither `group` nor `dm`), the endpoint

`POST /api/v1/channels/{channel_id}/messages/{message_id}/update` can be accessed with **read permission only**.

When `access_control` is set to `None`, the authorization check `has_access(..., type="read")` evaluates to `True`, allowing users who are **not the message owner** to update messages.

As a result, unauthorized modification of other users’ messages is possible.

---

## Attack Prerequisites

- The attacker is an authenticated user (role `user` or higher)
- The target channel is a standard channel (i.e., not `group` or `dm`)
- `access_control` is `None` or allows `read` access
- The attacker can obtain the target `message_id` (e.g., via the channel’s message list)



## Attack Scenario

1. The attacker (User B) retrieves another user’s `message_id` from the message list in a standard channel
2. The attacker sends a request to
    
    `POST /api/v1/channels/{channel_id}/messages/{message_id}/update`
    
3. The message authored by another user (User A) is successfully updated



## Potential Impact

- Unauthorized modification of other users’ messages (violation of data integrity)


# Steps to Reproduce

1. Log in as an administrator

<img width="3334" height="1668" alt="image" src="https://github.com/user-attachments/assets/b20323d3-c050-4438-8912-193a417654bc" />


2. Create User A

<img width="3346" height="788" alt="image" src="https://github.com/user-attachments/assets/b9e4fb8a-b14e-4a4b-b012-02ccfba52fca" />

3. Create User B

<img width="3354" height="796" alt="image" src="https://github.com/user-attachments/assets/f3cf6892-e6c9-4778-b471-f1cc0deec6c8" />


4. Log in as User A

<img width="3360" height="1668" alt="image" src="https://github.com/user-attachments/assets/5264ee07-f5c5-4bbe-ad4f-da69fb540fc9" />


5. Log in as User B

<img width="3354" height="1670" alt="image" src="https://github.com/user-attachments/assets/f112f8e8-b3e2-4e65-b226-c7b6c986f3bb" />


6. As the administrator, create a new channel

<img width="2582" height="988" alt="image" src="https://github.com/user-attachments/assets/bc012d9a-f884-4c83-b6bb-d1e5399f61bb" />


7. As User A, post a new message in the channel

<img width="2626" height="962" alt="image" src="https://github.com/user-attachments/assets/d7ff12c2-fe17-44f0-aaf9-5ce2bac9a378" />


8. As User B, edit User A’s message

<img width="2604" height="958" alt="image" src="https://github.com/user-attachments/assets/8e19ec3e-fdda-4d36-acd5-f3e1fd3402dd" />


9. Confirm that User A’s message has been modified without authorization

<img width="2378" height="1976" alt="image" src="https://github.com/user-attachments/assets/6415fd41-ac68-4d42-83c9-6297caee1fb4" />


## Affected Files and Line Numbers

- `backend/open_webui/routers/channels.py:1417–1460`
    
    The authorization check in `update_message_by_id` allows access with **read** permission
    
- `backend/open_webui/utils/access_control.py:124–135`
    
    When `access_control=None` and `strict=True`, **read** access is permitted
    
- `backend/open_webui/models/messages.py:341–358`
    
    The update logic does not enforce any message ownership check
    

## Recommended Mitigation

Update the condition in

`backend/open_webui/routers/channels.py:1451–1456`

by changing the permission check from **`read`** to **`write`**, so that only administrators, message owners, or users with write permission can update messages.

### Proposed Changes

- For standard channels, change the update permission requirement from
    
    `has_access(..., type="read")` to `has_access(..., type="write")`
    
- Preserve the existing ownership check (`message.user_id == user.id`)

## **AI Usage**

- Translation from Japanese to English
- CWE classification and assessment
- Affected Files and Line Numbers

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-jgj3-r8hr-9pjw
- https://nvd.nist.gov/vuln/detail/CVE-2026-44571
- https://github.com/open-webui/open-webui
