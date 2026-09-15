# [C] FreePBX Affected by Authentication Bypass Leading to SQL Injection and RCE

## Summary
Severity: Critical
Advisory: CVE-2025-57819
Aliases: GHSA-m42g-xg4c-5f3h
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-08-28
Source: https://osv.dev/vulnerability/CVE-2025-57819
Type: osv

## Details
FreePBX is an open-source web-based graphical user interface. FreePBX 15, 16, and 17 endpoints are vulnerable due to insufficiently sanitized user-supplied data allowing unauthenticated access to FreePBX Administrator leading to arbitrary database manipulation and remote code execution. This issue has been patched in endpoint versions 15.0.66, 16.0.89, and 17.0.3.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-57819
- https://community.freepbx.org/t/security-advisory-please-lock-down-your-administrator-access/107203
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57819.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-m42g-xg4c-5f3h
- https://nvd.nist.gov/vuln/detail/CVE-2025-57819
- https://github.com/watchtowrlabs/watchTowr-vs-FreePBX-CVE-2025-57819
