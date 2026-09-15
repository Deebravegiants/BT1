# [C] CVE-2021-42645

## Summary
Severity: Critical
Advisory: CVE-2021-42645
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-05-10
Source: https://osv.dev/vulnerability/CVE-2021-42645
Type: osv

## Details
CMSimple_XH 1.7.4 is affected by a remote code execution (RCE) vulnerability. To exploit this vulnerability, an attacker must use the "File" parameter to upload a PHP payload to get a reverse shell from the vulnerable host.

## References
- https://github.com/cmsimple-xh/cmsimple-xh/releases/tag/1.7.5
- https://github.com/Net-hunter121/CMSimple_XH-Unauth-RCE
