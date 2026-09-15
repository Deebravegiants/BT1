# [H] Leantime - JSON-RPC API Broken Access Control via users.getUser

## Summary
Severity: High
Advisory: CVE-2026-59712
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-59712
Type: osv

## Details
Leantime's Users::getUser method in the JSON-RPC API lacks proper authorization checks, allowing authenticated users to retrieve full user credential rows including password hashes, TOTP secrets, and session tokens. Attackers can exploit this by calling users.getUser with arbitrary user IDs to enumerate all accounts and obtain credentials for offline password cracking, 2FA bypass, and session hijacking.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59712.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59712
- https://www.vulncheck.com/advisories/leantime-credential-disclosure-via-unauthenticated-json-rpc-users-getuser-method
- https://github.com/Leantime/leantime/issues/3556
- https://github.com/Leantime/leantime/commit/4f2612d13e0e8a2093092a846b44506cf133b671
- https://github.com/Leantime/leantime
