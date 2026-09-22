# [C] CVE-2021-38140

## Summary
Severity: Critical
Advisory: CVE-2021-38140
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-10
Source: https://osv.dev/vulnerability/CVE-2021-38140
Type: osv

## Details
The set_user extension module before 2.0.1 for PostgreSQL allows a potential privilege escalation using RESET SESSION AUTHORIZATION after set_user().

## References
- https://github.com/pgaudit/set_user/releases/tag/REL2_0_1
- https://github.com/pgaudit/set_user/compare/REL2_0_0...REL2_0_1
