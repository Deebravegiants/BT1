# [M] IntegerOverflow leading to Out-Of-Bound Write Vulnerability in FreeRDP

## Summary
Severity: Medium
Advisory: CVE-2023-40186
Aliases: GHSA-hcj4-3c3r-5j3v
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2023-08-31
Source: https://osv.dev/vulnerability/CVE-2023-40186
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol (RDP), released under the Apache license. Affected versions are subject to an IntegerOverflow leading to Out-Of-Bound Write Vulnerability in the `gdi_CreateSurface` function. This issue affects FreeRDP based clients only. FreeRDP proxies are not affected as image decoding is not done by a proxy. This issue has been addressed in versions 2.11.0 and 3.0.0-beta3. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/FreeRDP/FreeRDP/blob/fee2b10ba1154f952769a53eb608f044782e22f8/libfreerdp/gdi/gfx.c#L1156-L1165
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/A6LLDAPEXRDJOM3PREDDD267SSNT77DP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IHMTGKCZXJPQOR5ZD2I4GPDNP2DKRXMF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OH2ATH2BKDNKCJAU4WPPXK4SHLE3UJUV/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40186.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-hcj4-3c3r-5j3v
- https://nvd.nist.gov/vuln/detail/CVE-2023-40186
- https://security.gentoo.org/glsa/202401-16
