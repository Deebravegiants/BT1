# [H] Plone Unauthorized Access Vulnerability

## Summary
Severity: High
Advisory: GHSA-qc57-h2f7-p4hx
CVE: CVE-2017-1000483
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qc57-h2f7-p4hx
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=2.5 <4.3.16
- PyPI: `Plone` — affected >=5.0 <5.1.0

## Details
Accessing private content via `str.format` in through-the-web templates and scripts in Plone 2.5-5.1rc1. This improves an earlier hotfix. Since the format method was introduced in Python 2.6, this part of the hotfix is only relevant for Plone 4 and 5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000483
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2018-72.yaml
- https://plone.org/security/hotfix/20171128/sandbox-escape
