# [H] py-lmdb Divide by Zero interruptions

## Summary
Severity: High
Advisory: GHSA-ggwq-vrgp-6gv4
CVE: CVE-2019-16228
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-ggwq-vrgp-6gv4
Type: github-advisory

## Affected
- PyPI: `lmdb` — affected >=0

## Details
An issue was discovered in py-lmdb 0.97. There is a divide-by-zero error in the function mdb_env_open2 if mdb_env_read_header obtains a zero value for a certain size field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16228
- https://github.com/TeamSeri0us/pocs/tree/master/lmdb/FPE
- https://github.com/jnwatson/py-lmdb
- https://github.com/pypa/advisory-database/tree/main/vulns/lmdb/PYSEC-2019-240.yaml
- https://pypi.org/project/lmdb
