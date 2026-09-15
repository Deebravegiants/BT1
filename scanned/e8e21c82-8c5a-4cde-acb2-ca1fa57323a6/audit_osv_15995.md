# [M] CVE-2019-2436

## Summary
Severity: Medium
Advisory: CVE-2019-2436
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2019-2436
Type: osv

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: Replication). Supported versions that are affected are 8.0.13 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.0 Base Score 5.5 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H).

## References
- http://www.securityfocus.com/bid/106625
- https://access.redhat.com/errata/RHSA-2019:2484
- https://access.redhat.com/errata/RHSA-2019:2511
- https://security.netapp.com/advisory/ntap-20190118-0002/
- http://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
