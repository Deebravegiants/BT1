# [H] Moodle XSS Vulnerability

## Summary
Severity: High
Advisory: GHSA-p7v9-gjrh-563x
CVE: CVE-2018-10891
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-p7v9-gjrh-563x
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.5.0 <3.5.1
- Packagist: `moodle/moodle` — affected >=3.4.0 <3.4.4
- Packagist: `moodle/moodle` — affected >=3.3.0 <3.3.7
- Packagist: `moodle/moodle` — affected >=3.2.0 <3.2.10
- Packagist: `moodle/moodle` — affected >=3.1.0 <3.1.13

## Details
A flaw was found in moodle before versions 3.5.1, 3.4.4, 3.3.7, 3.1.13. When a quiz question bank is imported, it was possible for the question preview that is displayed to execute JavaScript that is written into the question bank.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10891
- https://github.com/moodle/moodle/commit/0b18d0c960c27994dd9870d286f2da3fa5868c06
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10891
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=373371
- https://web.archive.org/web/20210124185945/https://www.securityfocus.com/bid/104739
