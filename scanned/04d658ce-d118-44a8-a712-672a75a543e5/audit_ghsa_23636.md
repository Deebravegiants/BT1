# [C] SaltStack Salt SQL Injection vulnerability in mysql.user_chpass function

## Summary
Severity: Critical
Advisory: GHSA-h8xp-h3jf-wv4v
CVE: CVE-2019-1010259
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h8xp-h3jf-wv4v
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=2018.3.0 <2018.3.4

## Details
SaltStack Salt 2018.3 is affected by: SQL Injection. The impact is: An attacker could escalate privileges on MySQL server deployed by cloud provider. It leads to RCE. The component is: The `mysql.user_chpass` function from the MySQL module for Salt (https://github.com/saltstack/salt/blob/develop/salt/modules/mysql.py#L1462). The attack vector is: specially crafted password string. The fixed version is: 2018.3.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1010259
- https://github.com/saltstack/salt/pull/51462
- https://github.com/ShantonRU/salt/commit/a46c86a987c78e74e87969d8d3b27094e6544b7a
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2019-119.yaml
- https://github.com/saltstack/salt
- https://github.com/saltstack/salt/blob/f22de0887cd7167887f113bf394244b74fb36b6b/salt/modules/mysql.py#L1534
