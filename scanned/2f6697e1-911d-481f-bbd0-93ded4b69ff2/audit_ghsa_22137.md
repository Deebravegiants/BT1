# [H] Subrion CMS vulnerable to CSRF in admin/blocks/add

## Summary
Severity: High
Advisory: GHSA-q4h5-g3w8-f9x7
CVE: CVE-2017-6068
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-q4h5-g3w8-f9x7
Type: github-advisory

## Affected
- Packagist: `intelliants/subrion` — affected >=0

## Details
Subrion CMS 4.0.5 has CSRF in `admin/blocks/add/`. The attacker can create any block, and can optionally insert XSS via the content parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6068
- https://github.com/intelliants/subrion
- https://web.archive.org/web/20210126223835/http://www.securityfocus.com/bid/97091
