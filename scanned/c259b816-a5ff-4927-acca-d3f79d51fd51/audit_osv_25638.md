# [M] FreeRDP Global-Buffer-Overflow in ncrush_decompress

## Summary
Severity: Medium
Advisory: CVE-2023-40589
Aliases: GHSA-gc34-mw6m-g42x
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2023-08-31
Source: https://osv.dev/vulnerability/CVE-2023-40589
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol (RDP), released under the Apache license. In affected versions there is a Global-Buffer-Overflow in the ncrush_decompress function. Feeding crafted input into this function can trigger the overflow which has only been shown to cause a crash. This issue has been addressed in versions 2.11.0 and 3.0.0-beta3. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/A6LLDAPEXRDJOM3PREDDD267SSNT77DP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IHMTGKCZXJPQOR5ZD2I4GPDNP2DKRXMF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OH2ATH2BKDNKCJAU4WPPXK4SHLE3UJUV/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40589.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-gc34-mw6m-g42x
- https://nvd.nist.gov/vuln/detail/CVE-2023-40589
- https://security.gentoo.org/glsa/202401-16
- https://github.com/FreeRDP/FreeRDP/commit/16141a30f983dd6f7a6e5b0356084171942c9416
