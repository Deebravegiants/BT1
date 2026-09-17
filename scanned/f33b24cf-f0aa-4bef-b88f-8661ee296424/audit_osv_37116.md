# [H] Chamilo LMS Vulnerable to Unauthenticated SQL Injection in chamiko-lms model.ajax.php

## Summary
Severity: High
Advisory: CVE-2026-28430
Aliases: GHSA-84gw-qjw9-v8jv
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/CVE-2026-28430
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to version 1.11.34, there is an unauthenticated SQL injection vulnerability which allows remote attackers to execute arbitrary SQL commands via the custom_dates parameter. By chaining this with a predictable legacy password reset mechanism, an attacker can achieve full administrative account takeover without any prior credentials. The vulnerability also exposes the entire database, including PII and system configurations. This issue has been patched in version 1.11.34.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v1.11.34
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28430.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-84gw-qjw9-v8jv
- https://nvd.nist.gov/vuln/detail/CVE-2026-28430
