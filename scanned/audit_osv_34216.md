# [H] CVE-2025-55912

## Summary
Severity: High
Advisory: CVE-2025-55912
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2025-55912
Type: osv

## Details
An issue in ClipBucket 5.5.0 and prior versions allows an unauthenticated attacker can exploit the plupload endpoint in photo_uploader.php to upload arbitrary files without any authentication, due to missing access controls in the upload handler

## References
- https://github.com/MacWarrior/clipbucket-v5/blob/5.5.0/upload/actions/photo_uploader.php
- https://github.com/MacWarrior/clipbucket-v5/tree/5.5.0
- https://medium.com/@mukund.s1337/cve-2025-55912-clipbucket-5-5-0-unauthenticated-arbitrary-file-upload-rce-720c0c0fbc58
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55912.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-55912
- https://github.com/MacWarrior/clipbucket-v5/releases?page=2
