# [H] Improper Access Control in MySQL Connector Python

## Summary
Severity: High
Advisory: GHSA-v5rq-w2xm-7g5f
CVE: CVE-2019-2435
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-v5rq-w2xm-7g5f
Type: github-advisory

## Affected
- PyPI: `mysql-connector-python` — affected >=8.0.0 <8.0.19
- PyPI: `mysql-connector-python` — affected >=2.1.0

## Details
Vulnerability in the MySQL Connectors component of Oracle MySQL (subcomponent: Connector/Python). Supported versions that are affected are 8.0.13 and prior and 2.1.8 and prior. Easily exploitable vulnerability allows unauthenticated attacker with network access via TLS to compromise MySQL Connectors. Successful attacks require human interaction from a person other than the attacker. Successful attacks of this vulnerability can result in unauthorized creation, deletion or modification access to critical data or all MySQL Connectors accessible data as well as unauthorized access to critical data or complete access to all MySQL Connectors accessible data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-2435
- https://github.com/mysql/mysql-connector-python
- https://security.netapp.com/advisory/ntap-20190118-0002
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00053.html
- http://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- http://www.securityfocus.com/bid/106616
