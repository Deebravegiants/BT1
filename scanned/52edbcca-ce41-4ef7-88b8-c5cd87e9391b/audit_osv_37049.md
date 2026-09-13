# [M] FreeRDP has possible Integer overflow in Stream_EnsureCapacity

## Summary
Severity: Medium
Advisory: CVE-2026-27951
Aliases: GHSA-qcfc-ghxr-h927
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27951
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to version 3.23.0, the function `Stream_EnsureCapacity` can create an endless blocking loop. This may affect all client and server implementations using `FreeRDP`. For practical exploitation this will only work on 32bit systems where the available physical memory is `>= SIZE_MAX`. Version 3.23.0 contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27951.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-qcfc-ghxr-h927
- https://nvd.nist.gov/vuln/detail/CVE-2026-27951
- https://github.com/FreeRDP/FreeRDP/commit/118afc0b954ba9d5632b7836ad24e454555ed113
