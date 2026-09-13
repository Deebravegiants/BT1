# [M] CVE-2021-2417

## Summary
Severity: Medium
Advisory: CVE-2021-2417
CVSS: 6.0 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:H)
Published: 2021-07-21
Source: https://osv.dev/vulnerability/CVE-2021-2417
Type: osv

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: GIS). Supported versions that are affected are 8.0.25 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as unauthorized update, insert or delete access to some of MySQL Server accessible data and unauthorized read access to a subset of MySQL Server accessible data. CVSS 3.1 Base Score 6.0 (Confidentiality, Integrity and Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:H).

## References
- https://security.netapp.com/advisory/ntap-20210723-0001/
- https://www.oracle.com/security-alerts/cpujul2021.html
