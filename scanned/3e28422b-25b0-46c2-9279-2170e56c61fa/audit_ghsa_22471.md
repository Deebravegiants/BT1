# [H] Dolibarr Cross-Site Request Forgery Vulnerability

## Summary
Severity: High
Advisory: GHSA-m66x-wm27-xxpc
CVE: CVE-2020-11825
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m66x-wm27-xxpc
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0

## Details
In Dolibarr 10.0.6, forms are protected with a Cross-Site Request Forgery (CSRF) token against CSRF attacks. The problem is any CSRF token in any user's session can be used in another user's session. CSRF tokens should not be valid in this situation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11825
- https://fatihhcelik.blogspot.com/2020/04/dolibarr-csrf.html
- https://github.com/Dolibarr/dolibarr
