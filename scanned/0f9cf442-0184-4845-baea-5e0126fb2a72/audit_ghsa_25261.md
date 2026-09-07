# [H] Improper Privilege Management in MySQL Connectors Java

## Summary
Severity: High
Advisory: GHSA-4vrv-ch96-6h42
CVE: CVE-2018-3258
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4vrv-ch96-6h42
Type: github-advisory

## Affected
- Maven: `mysql:mysql-connector-java` — affected >=0 <8.0.13

## Details
Vulnerability in the MySQL Connectors component of Oracle MySQL (subcomponent: Connector/J). Supported versions that are affected are 8.0.12 and prior. Easily exploitable vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Connectors. Successful attacks of this vulnerability can result in takeover of MySQL Connectors. CVSS 3.0 Base Score 8.8 (Confidentiality, Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3258
- https://access.redhat.com/errata/RHSA-2019:1545
- https://security.netapp.com/advisory/ntap-20181018-0002
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
