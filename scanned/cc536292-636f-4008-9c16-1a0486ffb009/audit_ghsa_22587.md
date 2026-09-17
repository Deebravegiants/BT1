# [H] Plaintext Storage of Sensitive Information in Laravel Log Viewer before v0.13.0

## Summary
Severity: High
Advisory: GHSA-63qj-p8gh-5xxx
CVE: CVE-2018-8947
CWE: CWE-312
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-63qj-p8gh-5xxx
Type: github-advisory

## Affected
- Packagist: `rap2hpoutre/laravel-log-viewer` — affected >=0 <0.13.0

## Details
rap2hpoutre Laravel Log Viewer before v0.13.0 relies on Base64 encoding for l, dl, and del requests, which makes it easier for remote attackers to bypass intended access restrictions, as demonstrated by reading arbitrary files via a dl request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8947
- https://github.com/rap2hpoutre/laravel-log-viewer/commit/cda89c06dc5331d06fab863d7cb1c4047ad68357
- https://github.com/rap2hpoutre/laravel-log-viewer/releases/tag/v0.13.0
- https://www.exploit-db.com/exploits/44343
