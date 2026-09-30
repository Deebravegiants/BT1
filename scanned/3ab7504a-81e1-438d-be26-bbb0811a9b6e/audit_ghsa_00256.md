# [H] cfscrape Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-5mc5-5j6c-qmf9
CVE: CVE-2017-7235
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-13
Source: https://github.com/advisories/GHSA-5mc5-5j6c-qmf9
Type: github-advisory

## Affected
- PyPI: `cfscrape` — affected >=1.6.6 <1.8.0

## Details
An issue was discovered in cloudflare-scrape 1.6.6 through 1.7.1. A malicious website owner could craft a page that executes arbitrary Python code against any cfscrape user who scrapes that website. This is fixed in 1.8.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7235
- https://github.com/Anorov/cloudflare-scrape/issues/97
- https://github.com/Anorov/cloudflare-scrape
- https://github.com/Anorov/cloudflare-scrape/releases/tag/1.8.0
- https://github.com/advisories/GHSA-5mc5-5j6c-qmf9
- https://github.com/pypa/advisory-database/tree/main/vulns/cfscrape/PYSEC-2017-7.yaml
- https://web.archive.org/web/20170701161512/http://www.securityfocus.com/bid/97191
