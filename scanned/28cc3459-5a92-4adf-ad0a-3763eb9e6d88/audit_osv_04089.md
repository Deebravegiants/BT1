# [M] Apache HTTP Server: HTTP Response Splitting in multiple modules

## Summary
Severity: Medium
Advisory: BIT-apache-2024-24795
Aliases: CVE-2024-24795
Ecosystem: Bitnami
Published: 2024-04-06
Source: https://osv.dev/vulnerability/BIT-apache-2024-24795
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.59

## Details
HTTP Response splitting in multiple modules in Apache HTTP Server allows an attacker that can inject malicious response headers into backend applications to cause an HTTP desynchronization attack.

Users are recommended to upgrade to version 2.4.59, which fixes this issue.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WNV4SZAPVS43DZWNFU7XBYYOZEZMI4ZC/
- https://security.netapp.com/advisory/ntap-20240415-0013/
- http://www.openwall.com/lists/oss-security/2024/04/04/5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/I2N2NZEX3MR64IWSGL3QGN7KSRUGAEMF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LX5U34KYGDYPRH3AJ6MDDCBJDWDPXNVJ/
- https://lists.debian.org/debian-lts-announce/2024/05/msg00013.html
- https://lists.debian.org/debian-lts-announce/2024/05/msg00014.html
- https://support.apple.com/kb/HT214119
- http://seclists.org/fulldisclosure/2024/Jul/18
- https://nvd.nist.gov/vuln/detail/CVE-2024-24795
