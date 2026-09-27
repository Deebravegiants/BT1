# [H] libpg_query memory leak

## Summary
Severity: High
Advisory: GHSA-vm3q-58wm-2r2x
CVE: CVE-2018-18482
CWE: CWE-772
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vm3q-58wm-2r2x
Type: github-advisory

## Affected
- PyPI: `pg-query` — affected >=0 <0.28
- PyPI: `pglast` — affected >=0 <0.28

## Details
An issue was discovered in libpg_query 10-1.0.2. There is a memory leak in pg_query_raw_parse in pg_query_parse.c, which might lead to a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18482
- https://github.com/lfittl/libpg_query/issues/49
- https://github.com/lelit/pglast
- https://github.com/pypa/advisory-database/tree/main/vulns/pg-query/PYSEC-2018-154.yaml
