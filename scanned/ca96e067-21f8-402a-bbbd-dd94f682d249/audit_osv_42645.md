# [M] Admidio before 5.0.11 Authentication Bypass via forum.php

## Summary
Severity: Medium
Advisory: CVE-2026-69091
Aliases: GHSA-cf48-6jrq-gjcm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-69091
Type: osv

## Details
Admidio before 5.0.11 contains an authentication bypass vulnerability in the forum module when configured in login-only mode. The access control logic in modules/forum.php fails to validate the login-only configuration state, allowing unauthenticated attackers to read forum topics and posts by directly accessing the module with read-only parameters.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-cf48-6jrq-gjcm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69091.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-69091
- https://www.vulncheck.com/advisories/admidio-before-authentication-bypass-via-forum-php
