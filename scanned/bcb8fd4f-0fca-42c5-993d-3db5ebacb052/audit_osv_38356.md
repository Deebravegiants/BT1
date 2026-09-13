# [H] ChurchCRM has a Blind SQL injection in EventNames.php

## Summary
Severity: High
Advisory: CVE-2026-39329
Aliases: GHSA-ggfm-5q4w-p93g
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39329
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to 7.1.0, an SQL injection vulnerability was identified in /EventNames.php in ChurchCRM. Authenticated users with AddEvent privileges can inject SQL via the newEvtTypeCntLst parameter during event type creation. The vulnerable flow reaches an ON DUPLICATE KEY UPDATE clause where unescaped user input is interpolated directly. This vulnerability is fixed in 7.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39329.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-ggfm-5q4w-p93g
- https://nvd.nist.gov/vuln/detail/CVE-2026-39329
