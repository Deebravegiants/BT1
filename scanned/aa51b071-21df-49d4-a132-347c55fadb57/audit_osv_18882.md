# [H] CVE-2020-36661

## Summary
Severity: High
Advisory: CVE-2020-36661
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-12
Source: https://osv.dev/vulnerability/CVE-2020-36661
Type: osv

## Details
A vulnerability was found in Kong lua-multipart 0.5.8-1. It has been declared as problematic. This vulnerability affects the function is_header of the file src/multipart.lua. The manipulation leads to inefficient regular expression complexity. Upgrading to version 0.5.9-1 is able to address this issue. The patch is identified as d632e5df43a2928fd537784a99a79dec288bf01b. It is recommended to upgrade the affected component. VDB-220642 is the identifier assigned to this vulnerability.

## References
- https://vuldb.com/?id.220642
- https://vuldb.com/?ctiid.220642
- https://github.com/Kong/lua-multipart/commit/d632e5df43a2928fd537784a99a79dec288bf01b
- https://github.com/Kong/lua-multipart/pull/34
- https://github.com/Kong/lua-multipart/releases/tag/0.5.9-1
