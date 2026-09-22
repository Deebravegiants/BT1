# [H] CVE-2020-14878

## Summary
Severity: High
Advisory: CVE-2020-14878
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-21
Source: https://osv.dev/vulnerability/CVE-2020-14878
Type: osv

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: Security: LDAP Auth). Supported versions that are affected are 8.0.21 and prior. Easily exploitable vulnerability allows low privileged attacker with access to the physical communication segment attached to the hardware where the MySQL Server executes to compromise MySQL Server. Successful attacks of this vulnerability can result in takeover of MySQL Server. CVSS 3.1 Base Score 8.0 (Confidentiality, Integrity and Availability impacts). CVSS Vector: (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H).

## References
- https://security.gentoo.org/glsa/202105-27
- https://security.netapp.com/advisory/ntap-20201023-0003/
- https://www.oracle.com/security-alerts/cpuoct2020.html
