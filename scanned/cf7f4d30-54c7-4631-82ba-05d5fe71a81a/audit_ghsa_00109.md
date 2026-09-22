# [C] SQL Injection in pycsw

## Summary
Severity: Critical
Advisory: GHSA-hg4c-rgvm-964g
CVE: CVE-2016-8640
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2018-08-15
Source: https://github.com/advisories/GHSA-hg4c-rgvm-964g
Type: github-advisory

## Affected
- PyPI: `pycsw` — affected >=2.0.0 <2.0.2
- PyPI: `pycsw` — affected >=0 <1.8.6
- PyPI: `pycsw` — affected >=1.10.0 <1.10.5

## Details
A SQL injection vulnerability in pycsw all versions before 2.0.2, 1.10.5 and 1.8.6 that leads to read and extract of any data from any table in the pycsw database that the database user has access to. Also on PostgreSQL (at least) it is possible to perform updates/inserts/deletes and database modifications to any table the database user has access to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-8640
- https://github.com/geopython/pycsw/pull/474/files
- https://github.com/geopython/pycsw/commit/522873e5ce48bb9cbd4e7e8168ca881ce709c222
- https://github.com/geopython/pycsw/commit/69546e13527c82e4f9191769215490381ad511b2
- https://github.com/geopython/pycsw/commit/daaf09b4b920708a415be3c7f446739661ba3753
- https://github.com/advisories/GHSA-hg4c-rgvm-964g
- https://github.com/geopython/pycsw
- https://github.com/pypa/advisory-database/tree/main/vulns/pycsw/PYSEC-2018-98.yaml
- https://patch-diff.githubusercontent.com/raw/geopython/pycsw/pull/474.patch
- http://seclists.org/oss-sec/2016/q4/406
