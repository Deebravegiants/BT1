# [M] FreeRDP Null Pointer Dereference leading denial of service

## Summary
Severity: Medium
Advisory: CVE-2023-39351
Aliases: GHSA-q9x9-cqjc-rgwq
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-08-31
Source: https://osv.dev/vulnerability/CVE-2023-39351
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol (RDP), released under the Apache license. Affected versions of FreeRDP are subject to a Null Pointer Dereference leading a crash in the RemoteFX (rfx) handling.  Inside the `rfx_process_message_tileset` function, the program allocates tiles using `rfx_allocate_tiles` for the number of numTiles. If the initialization process of tiles is not completed for various reasons, tiles will have a NULL pointer. Which may be accessed in further processing and would cause a program crash. This issue has been addressed in versions 2.11.0 and 3.0.0-beta3. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/A6LLDAPEXRDJOM3PREDDD267SSNT77DP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IHMTGKCZXJPQOR5ZD2I4GPDNP2DKRXMF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OH2ATH2BKDNKCJAU4WPPXK4SHLE3UJUV/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39351.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-q9x9-cqjc-rgwq
- https://nvd.nist.gov/vuln/detail/CVE-2023-39351
- https://security.gentoo.org/glsa/202401-16
