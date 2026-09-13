# [C] Pingvin Share X: TOTP Authentication Bypass via Password-only Login

## Summary
Severity: Critical
Advisory: CVE-2026-44196
Aliases: GHSA-j679-vp39-qwqq
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-44196
Type: osv

## Details
Pingvin Share X is a secure and easy self-hosted file sharing platform. From 1.14.1 to 1.16.2, a critical authentication bypass vulnerability allows an attacker who has obtained a valid username and password to skip the second-factor authentication (TOTP) requirement entirely. Although, an attacker still needs the user's password to reach this stage. This vulnerability is fixed in 1.16.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44196.json
- https://github.com/smp46/pingvin-share-x/security/advisories/GHSA-j679-vp39-qwqq
- https://nvd.nist.gov/vuln/detail/CVE-2026-44196
