# [H] Trytond allows modification of privileges of arbitrary users

## Summary
Severity: High
Advisory: GHSA-cqg4-rf29-3mv6
CVE: CVE-2012-0215
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-04
Source: https://github.com/advisories/GHSA-cqg4-rf29-3mv6
Type: github-advisory

## Affected
- PyPI: `trytond` — affected >=0 <2.4.0

## Details
`model/modelstorage.py` in the Tryton application framework (trytond) before 2.4.0 for Python does not properly restrict access to the Many2Many field in the relation model, which allows remote authenticated users to modify the privileges of arbitrary users via a (1) create, (2) write, (3) delete, or (4) copy rpc call.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-0215
- https://github.com/tryton/trytond/commit/d059ebb792401ded3129cd9402d7392dc34b81e3
- https://bugs.tryton.org/issue2476
- https://github.com/pypa/advisory-database/tree/main/vulns/trytond/PYSEC-2012-6.yaml
- https://github.com/tryton/trytond
- https://web.archive.org/web/20121113201043/http://news.tryton.org/2012/03/security-releases-for-all-supported.html
- http://hg.tryton.org/trytond/rev/8e64d52ecea4
- http://news.tryton.org/2012/03/security-releases-for-all-supported.html
- http://www.debian.org/security/2012/dsa-2444
