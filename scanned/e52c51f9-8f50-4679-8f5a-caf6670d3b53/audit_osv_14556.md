# [H] CVE-2019-10103

## Summary
Severity: High
Advisory: CVE-2019-10103
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-03
Source: https://osv.dev/vulnerability/CVE-2019-10103
Type: osv

## Details
JetBrains IntelliJ IDEA projects created using the Kotlin (JS Client/JVM Server) IDE Template were resolving Gradle artifacts using an http connection, potentially allowing an MITM attack. This issue, which was fixed in Kotlin plugin version 1.3.30, is similar to CVE-2019-10101.

## References
- https://blog.jetbrains.com/blog/2019/06/19/jetbrains-security-bulletin-q1-2019/
- https://security.netapp.com/advisory/ntap-20230818-0012/
