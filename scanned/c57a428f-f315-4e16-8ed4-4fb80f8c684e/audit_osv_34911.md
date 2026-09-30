# [H] Git for Windows leaks NTLM hash when cloning from an attacker-controlled server

## Summary
Severity: High
Advisory: CVE-2025-66413
Aliases: GHSA-hv9c-4jm9-jh3x
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2025-66413
Type: osv

## Details
Git for Windows is the Windows port of Git. Prior to 2.53.0(2), it is possible to obtain a user's NTLM hash by tricking them into cloning from a malicious server. Since NTLM hashing is weak, it is possible for the attacker to brute-force the user's account name and password. This vulnerability is fixed in 2.53.0(2).

## References
- https://github.com/git-for-windows/git/releases/tag/v2.53.0.windows.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66413.json
- https://github.com/git-for-windows/git/security/advisories/GHSA-hv9c-4jm9-jh3x
- https://nvd.nist.gov/vuln/detail/CVE-2025-66413
