# [C] CVE-2019-12736

## Summary
Severity: Critical
Advisory: CVE-2019-12736
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-02
Source: https://osv.dev/vulnerability/CVE-2019-12736
Type: osv

## Details
JetBrains Ktor framework before 1.2.0-rc does not sanitize the username provided by the user for the LDAP protocol, leading to command injection.

## References
- https://blog.jetbrains.com/blog/2019/09/26/jetbrains-security-bulletin-q2-2019/
