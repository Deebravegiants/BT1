# [M] pgAdmin 4 vulnerable to directory traversal 

## Summary
Severity: Medium
Advisory: GHSA-9crj-hpxh-f6qg
CVE: CVE-2023-0241
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-03-27
Source: https://github.com/advisories/GHSA-9crj-hpxh-f6qg
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <6.19

## Details
pgAdmin 4 versions prior to v6.19 contains a directory traversal vulnerability. A user of the product may change another user's settings or alter the database.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0241
- https://github.com/pgadmin-org/pgadmin4/issues/5734
- https://github.com/akshay-joshi/pgadmin4/commit/64d7289c5b3831137b17bb4c5022ef4f63d2ef42
- https://github.com/pgadmin-org
- https://jvn.jp/en/jp/JVN01398015
