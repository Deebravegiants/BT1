# [H] BIT-mariadb-2021-46669

## Summary
Severity: High
Advisory: BIT-mariadb-2021-46669
Aliases: BIT-mariadb-min-2021-46669, BIT-mysql-client-2021-46669, CVE-2021-46669
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2021-46669
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.4

## Details
MariaDB through 10.5.9 allows attackers to trigger a convert_const_to_int use-after-free when the BIGINT data type is used.

## References
- https://jira.mariadb.org/browse/MDEV-25638
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FRJCSPQHYPKTWXXZVDMY6JAHZJQ4TZ5X/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KHEOTQ63YWC3PGHGDFGS7AZIEXCGOPWH/
- https://mariadb.com/kb/en/security/
- https://security.netapp.com/advisory/ntap-20220221-0002/
- https://nvd.nist.gov/vuln/detail/CVE-2021-46669
