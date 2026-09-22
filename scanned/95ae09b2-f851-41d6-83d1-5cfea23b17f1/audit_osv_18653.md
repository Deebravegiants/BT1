# [C] CVE-2020-29592

## Summary
Severity: Critical
Advisory: CVE-2020-29592
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-14
Source: https://osv.dev/vulnerability/CVE-2020-29592
Type: osv

## Details
An issue was discovered in Orchard before 1.10. A broken access control issue in Orchard components that use the TinyMCE HTML editor's file upload allows an attacker to upload dangerous executables that bypass the file types allowed (regardless of the file types allowed list in Media settings).

## References
- https://github.com/OrchardCMS/Orchard/releases
- https://burninatorsec.blogspot.com/2021/04/cve-2020-29592-and-cve-2020-29593.html
