# [M] Missing offset validation leading to Out-of-Bounds Read in FreeRDP

## Summary
Severity: Medium
Advisory: CVE-2023-39356
Aliases: GHSA-q5v5-qhj5-mh6m
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-08-31
Source: https://osv.dev/vulnerability/CVE-2023-39356
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol (RDP), released under the Apache license. In affected versions a missing offset validation may lead to an Out Of Bound Read in the function `gdi_multi_opaque_rect`. In particular there is no code to validate if the value `multi_opaque_rect->numRectangles` is less than 45. Looping through `multi_opaque_rect->`numRectangles without proper boundary checks can lead to Out-of-Bounds Read errors which will likely lead to a crash. This issue has been addressed in versions 2.11.0 and 3.0.0-beta3. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/FreeRDP/FreeRDP/blob/63a2f65618748c12f79ff7450d46c6e194f2db76/include/freerdp/primary.h#L186-L196
- https://github.com/FreeRDP/FreeRDP/blob/63a2f65618748c12f79ff7450d46c6e194f2db76/libfreerdp/core/orders.c#L1503-L1504
- https://github.com/FreeRDP/FreeRDP/blob/63a2f65618748c12f79ff7450d46c6e194f2db76/libfreerdp/gdi/gdi.c#L723C1-L758
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/A6LLDAPEXRDJOM3PREDDD267SSNT77DP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IHMTGKCZXJPQOR5ZD2I4GPDNP2DKRXMF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OH2ATH2BKDNKCJAU4WPPXK4SHLE3UJUV/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39356.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-q5v5-qhj5-mh6m
- https://nvd.nist.gov/vuln/detail/CVE-2023-39356
- https://security.gentoo.org/glsa/202401-16
