# [M] User Enumeration via Distinct Error Messages in langgenius/dify-web

## Summary
Severity: Medium
Advisory: CVE-2025-11750
CVSS: 4.3 (CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2025-11750
Type: osv

## Details
In langgenius/dify-web version 1.6.0, the authentication mechanism reveals the existence of user accounts by returning different error messages for non-existent and existing accounts. Specifically, when a login or registration attempt is made with a non-existent username or email, the system responds with a message such as "account not found." Conversely, when the username or email exists but the password is incorrect, a different error message is returned. This discrepancy allows an attacker to enumerate valid user accounts by analyzing the error responses, potentially facilitating targeted social engineering, brute force, or credential stuffing attacks.

## References
- https://huntr.com/bounties/e7359f9f-c004-4304-9de9-753622d370a1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/11xxx/CVE-2025-11750.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-11750
