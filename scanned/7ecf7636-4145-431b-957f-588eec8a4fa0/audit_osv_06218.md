# [H] PHP-FPM memory access in root process leading to privilege escalation

## Summary
Severity: High
Advisory: BIT-libphp-2021-21703
Aliases: BIT-php-2021-21703, BIT-php-min-2021-21703, CVE-2021-21703
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2021-21703
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.0.0 <8.0.12

## Details
In PHP versions 7.3.x up to and including 7.3.31, 7.4.x below 7.4.25 and 8.0.x below 8.0.12, when running PHP FPM SAPI with main FPM daemon process running as root and child worker processes running as lower-privileged users, it is possible for the child processes to access memory shared with the main process and write to it, modifying it in a way that would cause the root process to conduct invalid memory reads and writes, which can be used to escalate privileges from local unprivileged user to the root user.

## References
- http://www.openwall.com/lists/oss-security/2021/10/26/7
- https://bugs.php.net/bug.php?id=81026
- https://lists.debian.org/debian-lts-announce/2021/10/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6PZVLICZUJMXOGWOUWSBAEGIVTF6Y6V3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JO5RA6YOBGGGKLIA6F6BQRZDDECF5L3R/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PBM3KKB3RY2YPOKNMC4HIH7IH3T3WC74/
- https://nvd.nist.gov/vuln/detail/CVE-2021-21703
- https://security.gentoo.org/glsa/202209-20
- https://security.netapp.com/advisory/ntap-20211118-0003/
- https://www.debian.org/security/2021/dsa-4992
- https://www.debian.org/security/2021/dsa-4993
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
