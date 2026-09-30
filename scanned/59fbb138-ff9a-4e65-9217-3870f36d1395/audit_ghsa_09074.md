# [M] Open WebUI has an Indirect Object Reference (IDOR) in user notes

## Summary
Severity: Medium
Advisory: GHSA-x3qm-p8hr-3c3h
CVE: CVE-2026-45666
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-x3qm-p8hr-3c3h
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.8.11

## Details
### Summary
The  API /api/v1/notes/{note_id} endpoint lacks proper authorization checks, allowing authenticated users to retrieve notes belonging to other users by guessing or enumerating UUIDs. This results in unauthorized disclosure of potentially sensitive or private user data.

### Details
- if notes is enabled from UI (Settings >> General >> Features >> Notes (Beta))
   - From API, attacker can access other user notes
- if notes is disabled from UI (Settings >> General >> Features >> Notes (Beta))
   - Then attacker can enable the notes from /api/config and access other user notes 

### PoC
- Step 1: Log in to the application as a valid user (User A).
![image](https://github.com/user-attachments/assets/3c4625f9-6e51-4cd1-942e-6a3f467520c0)

- Step 2: Intercept or inspect the response from the endpoint GET /api/config.
![image](https://github.com/user-attachments/assets/7c4fe716-314c-4640-bc9f-1e11ddc2273d)

- Step 3: Observe the field "enable_notes": false in the JSON response.
- Step 4: Manually change "enable_notes" to true using browser DevTools or by intercepting and modifying the response via a proxy like Burp Suite. (Please note, the occurrence of this API comes twice, hence modification needs to be made twice as well.)
![image](https://github.com/user-attachments/assets/99575570-a673-4508-b149-9a2480d8f62e)

- Step 5: Observe the loaded frontend application; the previously hidden notes form will now be visible.
![image](https://github.com/user-attachments/assets/a4059b1f-2e77-4f29-88a3-431e82b7c41d)

![image](https://github.com/user-attachments/assets/55e601d7-b013-43e3-a070-3a80f166e777)

- Step 6: Again, click on any note, intercept the request, and Replace the note_id in the URL with a different note ID known to belong to another user (e.g., by guessing or bruteforcing).
- Step 7: Send the modified request while remaining logged in as User A.
- Step 8: Observe that the server returns the content of another user's note, confirming unauthorized access.
![image](https://github.com/user-attachments/assets/cbec4ab5-a8a8-488a-a984-03e8de5b22f7)
![image](https://github.com/user-attachments/assets/046cd925-7299-44ba-bfc3-d6e7071d29d1)


### Impact
1. Unauthorized access to user-created notes
2. Possible exposure of confidential or sensitive uploaded data
3. Violation of user privacy and data isolation
4. High risk of legal or compliance breaches in regulated environments

## Resolution

Fixed in commit [de3317e26](https://github.com/open-webui/open-webui/commit/de3317e26bb67a2a7ea015a183bbd1d369880ebd), first released in **v0.8.11** (Mar 2026). All per-id note endpoints (`GET /api/v1/notes/{id}`, `POST /api/v1/notes/{id}/update`, `POST /api/v1/notes/{id}/access/update`, deletion) now enforce ownership: the handler fetches the note, then requires the caller to be admin, the note owner, or have an `AccessGrants` grant for the appropriate permission (`read` for retrieval, `write` for mutation). A non-owner with no grant receives 403.

Users on `>= 0.8.11` are not affected.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-x3qm-p8hr-3c3h
- https://nvd.nist.gov/vuln/detail/CVE-2026-45666
- https://github.com/open-webui/open-webui/commit/de3317e26bb67a2a7ea015a183bbd1d369880ebd
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.8.11
