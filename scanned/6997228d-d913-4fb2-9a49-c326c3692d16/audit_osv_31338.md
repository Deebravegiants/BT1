# [M] Insufficiently Protected Credentials in transformeroptimus/superagi

## Summary
Severity: Medium
Advisory: CVE-2024-9418
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-9418
Type: osv

## Details
In version 0.0.14 of transformeroptimus/superagi, the API endpoint `/api/users/get/{id}` returns the user's password in plaintext. This vulnerability allows an attacker to retrieve the password of another user, leading to potential account takeover.

## References
- https://huntr.com/bounties/9a8118a2-ea32-41f5-b501-fef4f31d8213
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/9xxx/CVE-2024-9418.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-9418
