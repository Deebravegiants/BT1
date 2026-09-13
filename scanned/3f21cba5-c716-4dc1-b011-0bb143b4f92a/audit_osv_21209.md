# [H] CVE-2021-41159

## Summary
Severity: High
Advisory: CVE-2021-41159
Aliases: GHSA-vh34-m9h7-95xq
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-10-21
Source: https://osv.dev/vulnerability/CVE-2021-41159
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol (RDP), released under the Apache license. All FreeRDP clients prior to version 2.4.1 using gateway connections (`/gt:rpc`) fail to validate input data. A malicious gateway might allow client memory to be written out of bounds. This issue has been resolved in version 2.4.1. If you are unable to update then use `/gt:http` rather than /gt:rdp connections if possible or use a direct connection without a gateway.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DWJXQOWKNR7O5HM2HFJOM4GBUFPTE3RG/
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-vh34-m9h7-95xq
- https://security.gentoo.org/glsa/202210-24
