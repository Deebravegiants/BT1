# [M] Mobile Security Framework (MobSF) Stored Cross-Site Scripting Vulnerability in "Diff or Compare" Functionality

## Summary
Severity: Medium
Advisory: GHSA-5jc6-h9w7-jm3p
CVE: CVE-2024-53999
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-12-03
Source: https://github.com/advisories/GHSA-5jc6-h9w7-jm3p
Type: github-advisory

## Affected
- PyPI: `mobsf` — affected >=0 <4.2.9

## Details
### Summary
The application allows users to upload files with scripts in the filename parameter. As a result, a malicious user can upload a script file to the system. When users in the application use the "Diff or Compare" functionality, they are affected by a Stored Cross-Site Scripting vulnerability.

### Details
I found a Stored Cross-Site Scripting vulnerability in the "Diff or Compare" functionality. This issue occurs because the upload functionality allows users to upload files with special characters such as <, >, /, and " in the filename. This vulnerability can be mitigated by restricting file uploads to filenames containing only whitelisted characters, such as A-Z, 0-9, and specific special characters permitted by business requirements, like - or _ . 

### PoC
_Complete instructions, including specific configuration details, to reproduce the vulnerability._
1. On MobSF version 4.2.8, I clicked on "Unload & Analyze" button.
![0](https://github.com/user-attachments/assets/489013fe-cf21-4839-bd39-35eebad01a3a)

2. I uploaded zip file as a name `test.zip`.
![1](https://github.com/user-attachments/assets/c26a18ec-c276-43d5-97df-fb189b8d5a6a)

3. I used an intercepting proxy tool while uploading a file and changed the value of the filename parameter from `test.zip` to `<image src onerror=prompt(document.domain)>test.zip`. This means I uploaded a file and set its name to a script value. As a result, the server allowed the file to be uploaded successfully.
![2](https://github.com/user-attachments/assets/90e275a2-58a4-4c0d-9b6a-399ec071cdf2)

4. I accessed /recent_scans/ and found a file named `<image src onerror=prompt(document.domain)>test.zip` in the recent scans. Then, I clicked on the "Differ or Compare" button."
![3](https://github.com/user-attachments/assets/0997a437-5841-49c1-ae94-e0e76173bdb6)

5. I found that the application requires selecting a file to compare, and I selected the file `<image src onerror=prompt(document.domain)>test.zip`
![4](https://github.com/user-attachments/assets/a156f058-732f-4763-8753-b0cef4075d53)

6. I found that the JavaScript in the filename value was executed in the web browser.
![5](https://github.com/user-attachments/assets/b0a9bcbf-af70-4ec6-a22d-6224dfc55639)


### Impact
Allowing a malicious user to upload a script in the filename parameter can be used to steal information from other users or administrators when they perform the compare functionality. The script will be stored in the system permanently in this vulnerability.

## References
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/security/advisories/GHSA-5jc6-h9w7-jm3p
- https://nvd.nist.gov/vuln/detail/CVE-2024-53999
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/commit/27d165872847f5ae7417caf09f37edeeba741e1e
- https://github.com/MobSF/Mobile-Security-Framework-MobSF
