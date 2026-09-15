# [H] SQL Injection in useredit.php

## Summary
Severity: High
Advisory: CVE-2022-21666
Aliases: GHSA-557p-hhpc-4wrx
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/CVE-2022-21666
Type: osv

## Details
Useful Simple Open-Source CMS (USOC) is a content management system (CMS) for programmers. Versions prior to Pb2.4Bfx3 allowed Sql injection in usersearch.php only for users with administrative privileges. Users should replace the file `admin/pages/useredit.php` with a newer version. USOC version Pb2.4Bfx3 contains a fixed version of `admin/pages/useredit.php`.

## References
- https://github.com/Aaron-Junker/USOC/releases/tag/Pb2.4Bfx3
- https://github.com/Aaron-Junker/USOC/security/advisories/GHSA-557p-hhpc-4wrx
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21666.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-21666
- https://github.com/Aaron-Junker/USOC/commit/c331d26aaab41a7e9e8c1c1a990132dca9d01e10
