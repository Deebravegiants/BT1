# [C] shlink has a Server-Side Request Forgery issue

## Summary
Severity: Critical
Advisory: GHSA-p85r-x2wj-mxqj
CVE: CVE-2026-50887
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-p85r-x2wj-mxqj
Type: github-advisory

## Affected
- Packagist: `shlinkio/shlink` — affected >=0

## Details
A Server-Side Request Forgery (SSRF) in the automatic short URL title resolution component of shlink v5.0.1 allows attackers to scan internal resources via supplying a crafted longUrl.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50887
- https://gist.github.com/pyuysig/9de95fb39eb089a4346570d791af99a6
- https://github.com/shlinkio/shlink
