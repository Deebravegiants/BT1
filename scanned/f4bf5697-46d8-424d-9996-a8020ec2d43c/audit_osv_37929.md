# [H] OpenEMR has SQL Injection in PostCalendar Category Delete

## Summary
Severity: High
Advisory: CVE-2026-33914
Aliases: GHSA-rq3v-38x5-3rm5
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-33914
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0.3, the PostCalendar module contains a blind SQL injection vulnerability in the `categoriesUpdate` administrative function. The `dels` POST parameter is read via `pnVarCleanFromInput()`, which only strips HTML tags and performs no SQL escaping. The value is then interpolated directly into a raw SQL `DELETE` statement that is executed unsanitized via Doctrine DBAL's `executeStatement()`. Version 8.0.0.3 patches the issue.

## References
- https://github.com/openemr/openemr/releases/tag/v8_0_0_3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33914.json
- https://github.com/openemr/openemr/security/advisories/GHSA-rq3v-38x5-3rm5
- https://nvd.nist.gov/vuln/detail/CVE-2026-33914
- https://github.com/openemr/openemr/commit/1b851fc9af84f181ad7a84210a168d0d568cd442
