# [H] FreeRDP Use-After-Free in RDPGFX_CMDID_RESETGRAPHICS

## Summary
Severity: High
Advisory: CVE-2023-39355
Aliases: GHSA-hvwj-vmg6-2f5h
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2023-08-31
Source: https://osv.dev/vulnerability/CVE-2023-39355
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol (RDP), released under the Apache license. Versions of FreeRDP on the 3.x release branch before beta3 are subject to a Use-After-Free in processing `RDPGFX_CMDID_RESETGRAPHICS` packets. If `context->maxPlaneSize` is 0, `context->planesBuffer` will be freed. However, without updating `context->planesBuffer`, this leads to a Use-After-Free exploit vector. In most environments this should only result in a crash. This issue has been addressed in version 3.0.0-beta3 and users of the beta 3.x releases are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39355.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-hvwj-vmg6-2f5h
- https://nvd.nist.gov/vuln/detail/CVE-2023-39355
- https://security.gentoo.org/glsa/202401-16
- https://github.com/FreeRDP/FreeRDP/commit/d6f9d33a7db0b346195b6a15b5b99944ba41beee
