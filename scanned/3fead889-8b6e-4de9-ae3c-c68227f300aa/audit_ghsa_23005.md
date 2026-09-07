# [M] Lin-CMS-Flask Cross Site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rvf8-c35m-8289
CVE: CVE-2020-18699
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rvf8-c35m-8289
Type: github-advisory

## Affected
- PyPI: `lin-cms` — affected >=0

## Details
Cross Site Scripting (XSS) in Lin-CMS-Flask v0.1.1 allows remote attackers to execute arbitrary code by entering scripts in the the 'Username' parameter of the in component 'app/api/cms/user.py'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-18699
- https://github.com/TaleLin/lin-cms-flask/issues/28
- https://github.com/TaleLin/lin-cms-flask
- https://github.com/pypa/advisory-database/tree/main/vulns/lin-cms/PYSEC-2021-340.yaml
