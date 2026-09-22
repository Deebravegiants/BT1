# [M] GeniXCMS XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pwr7-j6g3-hmx6
CVE: CVE-2017-17431
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-pwr7-j6g3-hmx6
Type: github-advisory

## Affected
- Packagist: `genix/cms` — affected >=0

## Details
GeniXCMS 1.1.5 has XSS via the from, id, lang, menuid, mod, q, status, term, to, or token parameter. NOTE: this might overlap CVE-2017-14761, CVE-2017-14762, or CVE-2017-14765.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17431
- https://code610.blogspot.com/2017/12/modus-operandi-genixcms-115.html
- https://github.com/semplon/GeniXCMS
