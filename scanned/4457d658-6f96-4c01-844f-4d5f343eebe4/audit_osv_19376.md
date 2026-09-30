# [M] CVE-2021-2046

## Summary
Severity: Medium
Advisory: CVE-2021-2046
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2021-01-20
Source: https://osv.dev/vulnerability/CVE-2021-2046
Type: osv

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: Stored Procedure). Supported versions that are affected are 8.0.22 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. While the vulnerability is in MySQL Server, attacks may significantly impact additional products. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.1 Base Score 6.8 (Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H).

## References
- https://security.gentoo.org/glsa/202105-27
- https://security.netapp.com/advisory/ntap-20210219-0003/
- https://www.oracle.com/security-alerts/cpujan2021.html
