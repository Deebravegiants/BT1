# [C] Lin-CMS-Flask vulnerable to Improper Authentication

## Summary
Severity: Critical
Advisory: GHSA-h6r2-pgvx-683c
CVE: CVE-2020-18698
CWE: CWE-307
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h6r2-pgvx-683c
Type: github-advisory

## Affected
- PyPI: `Lin-CMS` — affected 0.1.1

## Details
Improper Authentication in Lin-CMS-Flask v0.1.1 allows remote attackers to launch brute force login attempts without restriction via the 'login' function in the component `app/api/cms/user.py`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-18698
- https://github.com/TaleLin/lin-cms-flask/issues/27
- https://cwe.mitre.org/data/definitions/307.html
- https://github.com/TaleLin/lin-cms-flask
- https://github.com/pypa/advisory-database/tree/main/vulns/lin-cms/PYSEC-2021-339.yaml
