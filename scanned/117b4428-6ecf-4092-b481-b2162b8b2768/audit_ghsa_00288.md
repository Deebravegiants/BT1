# [M] Pysaml2 improperly initializes encryption vector

## Summary
Severity: Medium
Advisory: GHSA-cq94-qf6q-mf2h
CVE: CVE-2017-1000246
CWE: CWE-330
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2018-07-16
Source: https://github.com/advisories/GHSA-cq94-qf6q-mf2h
Type: github-advisory

## Affected
- PyPI: `pysaml2` — affected >=0 <4.6.0

## Details
Python package pysaml2 version 4.5.0 and earlier reuses the initialization vector across encryptions in the IDP server, resulting in weak encryption of data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000246
- https://github.com/rohe/pysaml2/issues/417
- https://github.com/IdentityPython/pysaml2/pull/519/commits/7323f5c20efb59424d853c822e7a26d1aa3e84aa
- https://github.com/pypa/advisory-database/tree/main/vulns/pysaml2/PYSEC-2017-26.yaml
- https://github.com/rohe/pysaml2
