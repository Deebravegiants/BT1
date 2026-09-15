# [H] Information Disclosure in transformeroptimus/superagi

## Summary
Severity: High
Advisory: CVE-2024-10267
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10267
Type: osv

## Details
An information disclosure vulnerability exists in the latest version of transformeroptimus/superagi. An attacker can leak sensitive user information, including names, emails, and passwords, by attempting to register a new account with an email that is already in use. The server returns all information associated with the existing account. The vulnerable endpoint is located in the user registration functionality.

## References
- https://huntr.com/bounties/13da8366-4670-4d46-9f5a-ba3f642b692e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10267.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10267
