# [M] Cross-Site Request Forgery in JupyterHub

## Summary
Severity: Medium
Advisory: GHSA-7xx3-qp5w-fw96
CVE: CVE-2020-36191
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7xx3-qp5w-fw96
Type: github-advisory

## Affected
- PyPI: `jupyterhub` — affected >=0 <1.2.0b1

## Details
JupyterHub 1.1.0 allows CSRF in the admin panel via a request that lacks an `_xsrf` field, as demonstrated by a /hub/api/user request (to add or remove a user account).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36191
- https://github.com/jupyterhub/jupyterhub/issues/3304
- https://github.com/advisories/GHSA-7xx3-qp5w-fw96
- https://github.com/jupyterhub/jupyterhub
- https://github.com/jupyterhub/jupyterhub/releases
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyterhub/PYSEC-2021-67.yaml
