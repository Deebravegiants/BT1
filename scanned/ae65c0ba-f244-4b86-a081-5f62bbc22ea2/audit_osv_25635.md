# [M] Out-Of-Bounds Write in FreeRDP

## Summary
Severity: Medium
Advisory: CVE-2023-40567
Aliases: GHSA-2w9f-8wg4-8jfp
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2023-08-31
Source: https://osv.dev/vulnerability/CVE-2023-40567
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol (RDP), released under the Apache license. Affected versions are subject to an Out-Of-Bounds Write in the `clear_decompress_bands_data` function in which there is no offset validation. Abuse of this vulnerability may lead to an out of bounds write. This issue has been addressed in versions 2.11.0 and 3.0.0-beta3. Users are advised to upgrade. there are no known workarounds for this vulnerability.

## References
- https://github.com/FreeRDP/FreeRDP/blob/5be5553e0da72178a4b94cc1ffbdace9ceb153e5/libfreerdp/codec/clear.c#L612-L618
- https://github.com/FreeRDP/FreeRDP/blob/5be5553e0da72178a4b94cc1ffbdace9ceb153e5/libfreerdp/codec/clear.c#L843-L845
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/A6LLDAPEXRDJOM3PREDDD267SSNT77DP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IHMTGKCZXJPQOR5ZD2I4GPDNP2DKRXMF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OH2ATH2BKDNKCJAU4WPPXK4SHLE3UJUV/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40567.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-2w9f-8wg4-8jfp
- https://nvd.nist.gov/vuln/detail/CVE-2023-40567
- https://security.gentoo.org/glsa/202401-16
