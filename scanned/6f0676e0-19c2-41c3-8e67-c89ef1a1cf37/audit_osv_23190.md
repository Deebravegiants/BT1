# [H] CVE-2022-44789

## Summary
Severity: High
Advisory: CVE-2022-44789
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-11-23
Source: https://osv.dev/vulnerability/CVE-2022-44789
Type: osv

## Details
A logical issue in O_getOwnPropertyDescriptor() in Artifex MuJS 1.0.0 through 1.3.x before 1.3.2 allows an attacker to achieve Remote Code Execution through memory corruption, via the loading of a crafted JavaScript file.

## References
- https://github.com/alalng/CVE-2022-44789/blob/main/PublicReferenceURL.txt
- https://github.com/ccxvii/mujs/releases/tag/1.3.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/44xxx/CVE-2022-44789.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MC6PLHTXHZ7GW7QQGTLBHLXL47UHTHXO/
- https://nvd.nist.gov/vuln/detail/CVE-2022-44789
- https://www.debian.org/security/2022/dsa-5291
- https://github.com/ccxvii/mujs/commit/edb50ad66f7601ca9a3544a0e9045e8a8c60561f
