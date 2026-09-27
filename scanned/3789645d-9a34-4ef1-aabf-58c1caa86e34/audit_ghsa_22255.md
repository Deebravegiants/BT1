# [C] py-lmdb Invalid write operation

## Summary
Severity: Critical
Advisory: GHSA-9q62-r72g-pvv7
CVE: CVE-2019-16224
CWE: CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9q62-r72g-pvv7
Type: github-advisory

## Affected
- PyPI: `lmdb` — affected >=0

## Details
An issue was discovered in py-lmdb 0.97. For certain values of `md_flags`, `mdb_node_add` does not properly set up a memcpy destination, leading to an invalid write operation. NOTE: this outcome occurs when accessing a `data.mdb` file supplied by an attacker.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16224
- https://github.com/TeamSeri0us/pocs/tree/master/lmdb/lmdb%20initialization%20vuln
- https://github.com/jnwatson/py-lmdb
- https://github.com/pypa/advisory-database/tree/main/vulns/lmdb/PYSEC-2019-236.yaml
- https://pypi.org/project/lmdb
