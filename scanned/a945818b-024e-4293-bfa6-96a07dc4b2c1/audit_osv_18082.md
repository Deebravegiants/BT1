# [H] CVE-2020-23829

## Summary
Severity: High
Advisory: CVE-2020-23829
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-01
Source: https://osv.dev/vulnerability/CVE-2020-23829
Type: osv

## Details
interface/new/new_comprehensive_save.php in LibreHealth EHR 2.0.0 suffers from an authenticated file upload vulnerability, allowing remote attackers to achieve remote code execution (RCE) on the hosting webserver by uploading a maliciously crafted image.

## References
- https://github.com/boku7/LibreHealth-authRCE
- https://www.exploit-db.com/exploits/48702
