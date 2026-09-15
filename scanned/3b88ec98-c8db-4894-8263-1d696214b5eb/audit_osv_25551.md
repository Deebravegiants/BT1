# [M] Invalid offset validation leading to Out Of Bound Write in FreeRDP

## Summary
Severity: Medium
Advisory: CVE-2023-39352
Aliases: GHSA-whwr-qcf2-2mvj
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-08-31
Source: https://osv.dev/vulnerability/CVE-2023-39352
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol (RDP), released under the Apache license. Affected versions are subject to an invalid offset validation leading to Out Of Bound Write. This can be triggered when the values `rect->left` and `rect->top` are exactly equal to `surface->width` and  `surface->height`. eg. `rect->left` == `surface->width` && `rect->top` == `surface->height`. In practice this should cause a crash. This issue has been addressed in versions 2.11.0 and 3.0.0-beta3. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/FreeRDP/FreeRDP/blob/63a2f65618748c12f79ff7450d46c6e194f2db76/libfreerdp/gdi/gfx.c#L1219-L1239
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/A6LLDAPEXRDJOM3PREDDD267SSNT77DP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IHMTGKCZXJPQOR5ZD2I4GPDNP2DKRXMF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OH2ATH2BKDNKCJAU4WPPXK4SHLE3UJUV/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39352.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-whwr-qcf2-2mvj
- https://nvd.nist.gov/vuln/detail/CVE-2023-39352
- https://security.gentoo.org/glsa/202401-16
