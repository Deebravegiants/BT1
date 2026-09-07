# [H] LMDB invalid write 

## Summary
Severity: High
Advisory: GHSA-r8g9-w4f3-9crm
CVE: CVE-2019-16226
CWE: CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r8g9-w4f3-9crm
Type: github-advisory

## Affected
- PyPI: `lmdb` — affected >=0

## Details
An issue was discovered in py-lmdb 0.97. `mdb_node_del` does not validate a `memmove` in the case of an unexpected `node->mn_hi`, leading to an invalid write operation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16226
- https://github.com/jnwatson/py-lmdb/issues/210
- https://github.com/LMDB/lmdb/blob/mdb.master/libraries/liblmdb/mdb.c#L8443-L8498
- https://github.com/TeamSeri0us/pocs/tree/master/lmdb/lmdb%20memory%20corruption%20vuln
- https://github.com/jnwatson/py-lmdb
- https://github.com/pypa/advisory-database/tree/main/vulns/lmdb/PYSEC-2019-238.yaml
- https://pypi.org/project/lmdb
