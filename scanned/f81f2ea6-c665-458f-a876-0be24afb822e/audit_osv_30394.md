# [M] Exposure of Sensitive Information in mintplex-labs/anything-llm

## Summary
Severity: Medium
Advisory: CVE-2024-5213
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2024-5213
Type: osv

## Details
In mintplex-labs/anything-llm versions up to and including 1.5.3, an issue was discovered where the password hash of a user is returned in the response after login (`POST /api/request-token`) and after account creations (`POST /api/admin/users/new`). This exposure occurs because the entire User object, including the bcrypt password hash, is included in the response sent to the frontend. This practice could potentially lead to sensitive information exposure despite the use of bcrypt, a strong hashing algorithm. It is recommended not to expose any clues about passwords to the frontend.

## References
- https://huntr.com/bounties/8794fb65-50aa-40e3-b348-a29838dbf63d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5213.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5213
- https://github.com/mintplex-labs/anything-llm/commit/9df4521113ddb9a3adb5d0e3941e7d494992629c
