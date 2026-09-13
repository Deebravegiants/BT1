# [M] BIT-mariadb-2020-2574

## Summary
Severity: Medium
Advisory: BIT-mariadb-2020-2574
Aliases: BIT-mariadb-min-2020-2574, BIT-mysql-client-2020-2574, CVE-2020-2574
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2020-2574
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.4.0 <10.4.12

## Details
Vulnerability in the MySQL Client product of Oracle MySQL (component: C API). Supported versions that are affected are 5.6.46 and prior, 5.7.28 and prior and 8.0.18 and prior. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise MySQL Client. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Client. CVSS 3.0 Base Score 5.9 (Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H).

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00007.html
- http://www.openwall.com/lists/oss-security/2020/09/29/1
- https://security.gentoo.org/glsa/202105-27
- https://security.netapp.com/advisory/ntap-20200122-0002/
- https://usn.ubuntu.com/4250-1/
- https://usn.ubuntu.com/4250-2/
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-2574
