# [M] Stored cross-site scripting in PressBooks

## Summary
Severity: Medium
Advisory: GHSA-9652-78hp-w58c
CVE: CVE-2021-3271
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-9652-78hp-w58c
Type: github-advisory

## Affected
- Packagist: `pressbooks/pressbooks` — affected >=0 <5.18.0

## Details
PressBooks 5.17.3 contains a cross-site scripting (XSS). Stored XSS can be submitted via the Book Info's Long Description Body, and all actions to open or preview the books page will result in the triggering the stored XSS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3271
- https://github.com/pressbooks/pressbooks/pull/2072
- https://github.com/pressbooks/pressbooks/commit/941a8c5eaeacea5eb211b54ee55bc0348139cbd8
- https://github.com/pressbooks/pressbooks
- https://www.gosecure.net/blog/2021/02/16/cve-2021-3271-pressbooks-stored-cross-site-scripting-proof-of-concept
