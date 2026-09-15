# [M] CVE-2019-2991

## Summary
Severity: Medium
Advisory: CVE-2019-2991
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2019-10-16
Source: https://osv.dev/vulnerability/CVE-2019-2991
Type: osv

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: Optimizer). Supported versions that are affected are 8.017 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.0 Base Score 5.5 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6DTUCXX5XXPNPFV2PHP6IESGTCFMZOFP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7X5D3O4TOQ57KL5FLQEXH2JB2UQYHCUZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MKCJLNRK6RHFAHV7ZFD3XO7HNSBU3XOL/
- https://security.netapp.com/advisory/ntap-20191017-0002/
- https://usn.ubuntu.com/4195-1/
- http://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
