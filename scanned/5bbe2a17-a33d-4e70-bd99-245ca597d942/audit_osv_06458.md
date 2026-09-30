# [M] BIT-mariadb-2020-14550

## Summary
Severity: Medium
Advisory: BIT-mariadb-2020-14550
Aliases: BIT-mariadb-min-2020-14550, BIT-mysql-client-2020-14550, CVE-2020-14550
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2020-14550
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.2.0 <10.2.15

## Details
Vulnerability in the MySQL Client product of Oracle MySQL (component: C API). Supported versions that are affected are 5.6.48 and prior, 5.7.30 and prior and 8.0.20 and prior. Difficult to exploit vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Client. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Client. CVSS 3.1 Base Score 5.3 (Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CAI7GRYZ5265JVKHC6VXI57MNJDDB63C/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HYQPCHGCVKFS3H226QQKZFQP56JYOQ3T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SA2XMR2ZY2BPR3VLTDVLNV74JL7TA7KL/
- https://security.gentoo.org/glsa/202105-27
- https://security.netapp.com/advisory/ntap-20210622-0001/
- https://usn.ubuntu.com/4441-1/
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-14550
