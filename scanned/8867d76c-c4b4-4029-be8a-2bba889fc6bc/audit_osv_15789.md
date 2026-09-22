# [C] CVE-2019-19683

## Summary
Severity: Critical
Advisory: CVE-2019-19683
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-12-09
Source: https://osv.dev/vulnerability/CVE-2019-19683
Type: osv

## Details
RoxyFileman, as shipped with nopCommerce v4.2.0, is vulnerable to ../ path traversal via d or f to Admin/RoxyFileman/ProcessRequest because of Libraries/Nop.Services/Media/RoxyFileman/FileRoxyFilemanService.cs.

## References
- https://github.com/klezVirus/cves/tree/master/NopCommerce/Privilege%20Escalation%20via%20Path%20Traversal
