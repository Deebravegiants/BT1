# [H] geopandas SQL Injection Vulnerability in to_postgis() Allows Information Disclosure

## Summary
Severity: High
Advisory: GHSA-6497-prx7-gpmq
CVE: CVE-2025-69662
CWE: CWE-202, CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-30
Source: https://github.com/advisories/GHSA-6497-prx7-gpmq
Type: github-advisory

## Affected
- PyPI: `geopandas` — affected >=0 <1.1.2

## Details
SQL injection vulnerability in geopandas before v.1.1.2 allows an attacker to obtain sensitive information via the to_postgis()` function being used to write GeoDataFrames to a PostgreSQL database.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-69662
- https://github.com/geopandas/geopandas/issues/3679
- https://github.com/geopandas/geopandas/pull/3681
- https://github.com/geopandas/geopandas/commit/6aa8ef14ffdee4ba1044349ab948e1a1fbfaf419
- https://aydinnyunus.github.io/2025/12/27/sql-injection-geopandas
- https://github.com/geopandas/geopandas
- https://github.com/geopandas/geopandas/releases/tag/v1.1.2
- https://github.com/pypa/advisory-database/tree/main/vulns/geopandas/PYSEC-2026-62.yaml
- https://lists.debian.org/debian-lts-announce/2026/04/msg00025.html
