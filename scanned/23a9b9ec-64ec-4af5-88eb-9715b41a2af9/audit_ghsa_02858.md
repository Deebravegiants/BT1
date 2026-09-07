# [M] Cross-site Scripting in shuup

## Summary
Severity: Medium
Advisory: GHSA-5pcx-vqjp-p34w
CVE: CVE-2021-25963
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-10-04
Source: https://github.com/advisories/GHSA-5pcx-vqjp-p34w
Type: github-advisory

## Affected
- PyPI: `shuup` — affected >=1.6.0 <2.11.0

## Details
In Shuup, versions 1.6.0 through 2.10.8 are vulnerable to reflected Cross-Site Scripting (XSS) that allows execution of arbitrary javascript code on a victim browser. This vulnerability exists due to the error page contents not escaped.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25963
- https://github.com/shuup/shuup/commit/75714c37e32796eb7cbb0d977af5bcaa26573588
- https://github.com/pypa/advisory-database/tree/main/vulns/shuup/PYSEC-2021-350.yaml
- https://github.com/shuup/shuup
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25963
