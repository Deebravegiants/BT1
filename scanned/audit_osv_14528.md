# [H] CVE-2019-10101

## Summary
Severity: High
Advisory: CVE-2019-10101
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-03
Source: https://osv.dev/vulnerability/CVE-2019-10101
Type: osv

## Details
JetBrains Kotlin versions before 1.3.30 were resolving artifacts using an http connection during the build process, potentially allowing an MITM attack.

## References
- https://blog.jetbrains.com/blog/2019/06/19/jetbrains-security-bulletin-q1-2019/
- https://security.netapp.com/advisory/ntap-20230818-0012/
- https://medium.com/bugbountywriteup/want-to-take-over-the-java-ecosystem-all-you-need-is-a-mitm-1fc329d898fb
