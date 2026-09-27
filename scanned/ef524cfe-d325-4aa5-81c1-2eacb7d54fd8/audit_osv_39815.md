# [H] TypeBot API tokens stored in plaintext

## Summary
Severity: High
Advisory: CVE-2026-47702
Aliases: GHSA-9c96-gcg3-2662
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-47702
Type: osv

## Details
TypeBot is a chatbot builder tool. In version 3.16.1, API tokens (bearer credentials used to authenticate against the builder API) are stored in the database as cleartext strings. An attacker who gains read access to the database (e.g., via SQL injection, backup exposure, or insider access) can extract all API tokens and impersonate any user without requiring a password or multi-factor authentication. Version 3.17.0 fixes the issue.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47702.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-9c96-gcg3-2662
- https://nvd.nist.gov/vuln/detail/CVE-2026-47702
- https://github.com/baptisteArno/typebot.io/commit/fdcc1784c9318904c180703e1ef4f1e06e6dd50e
- https://github.com/baptisteArno/typebot.io/pull/2492
