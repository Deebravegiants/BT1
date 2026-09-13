# [H] CVE-2019-10102

## Summary
Severity: High
Advisory: CVE-2019-10102
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-03
Source: https://osv.dev/vulnerability/CVE-2019-10102
Type: osv

## Details
JetBrains Ktor framework (created using the Kotlin IDE template) versions before 1.1.0 were resolving artifacts using an http connection during the build process, potentially allowing an MITM attack. This issue was fixed in Kotlin plugin version 1.3.30.

## References
- https://blog.jetbrains.com/blog/2019/06/19/jetbrains-security-bulletin-q1-2019/
- https://security.netapp.com/advisory/ntap-20230818-0012/
