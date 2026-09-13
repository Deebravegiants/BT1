# [H] CVE-2019-25087

## Summary
Severity: High
Advisory: CVE-2019-25087
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-12-27
Source: https://osv.dev/vulnerability/CVE-2019-25087
Type: osv

## Details
A vulnerability was found in RamseyK httpserver. It has been rated as critical. This issue affects the function ResourceHost::getResource of the file src/ResourceHost.cpp of the component URI Handler. The manipulation of the argument uri leads to path traversal: '../filedir'. The attack may be initiated remotely. The name of the patch is 1a0de56e4dafff9c2f9c8f6b130a764f7a50df52. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-216863.

## References
- https://vuldb.com/?ctiid.216863
- https://vuldb.com/?id.216863
- https://github.com/RamseyK/httpserver/commit/1a0de56e4dafff9c2f9c8f6b130a764f7a50df52
