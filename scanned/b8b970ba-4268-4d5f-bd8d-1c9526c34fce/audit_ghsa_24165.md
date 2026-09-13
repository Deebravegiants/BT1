# [H] Tryton vulnerable to arbitrary command execution

## Summary
Severity: High
Advisory: GHSA-m9jj-5qvj-5fhx
CVE: CVE-2014-6633
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-m9jj-5qvj-5fhx
Type: github-advisory

## Affected
- PyPI: `tryton` — affected >=0 <2.4.15
- PyPI: `tryton` — affected >=2.6.0 <2.6.14
- PyPI: `tryton` — affected >=2.8.0 <2.8.11
- PyPI: `tryton` — affected >=3.2.0 <3.2.3
- PyPI: `trytond` — affected >=2.4.0 <2.4.15
- PyPI: `trytond` — affected >=2.6.0 <2.6.14
- PyPI: `trytond` — affected >=2.8.0 <2.8.11
- PyPI: `trytond` — affected >=3.2.0 <3.2.3
- PyPI: `trytond` — affected >=3.0.0 <3.0.7

## Details
The `safe_eval` function in trytond in Tryton before 2.4.15, 2.6.x before 2.6.14, 2.8.x before 2.8.11, 3.0.x before 3.0.7, and 3.2.x before 3.2.3 allows remote authenticated users to execute arbitrary commands via shell metacharacters in (1) the `collection.domain` in the webdav module or (2) the formula field in the `price_list` module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-6633
- https://github.com/tryton/trytond/commit/19fc2a01357b7638041953326e404f51d96fad06
- https://github.com/tryton/trytond/commit/3e4c2b7e8c7b3358597a0d484fa98f45483ee92a
- https://bugs.tryton.org/issue4155
- https://github.com/pypa/advisory-database/tree/main/vulns/trytond/PYSEC-2018-59.yaml
- https://github.com/tryton/trytond
- http://www.tryton.org/posts/security-release-for-issue4155.html
