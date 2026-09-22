# [M] Incorrect offset calculation leading to denial of service in FreeRDP

## Summary
Severity: Medium
Advisory: CVE-2023-39350
Aliases: GHSA-rrrv-3w42-pffh
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-08-31
Source: https://osv.dev/vulnerability/CVE-2023-39350
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol (RDP), released under the Apache license. This issue affects Clients only. Integer underflow leading to DOS (e.g. abort due to `WINPR_ASSERT` with default compilation flags). When an insufficient blockLen is provided, and proper length validation is not performed, an Integer Underflow occurs, leading to a Denial of Service (DOS) vulnerability. This issue has been addressed in versions 2.11.0 and 3.0.0-beta3. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/A6LLDAPEXRDJOM3PREDDD267SSNT77DP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IHMTGKCZXJPQOR5ZD2I4GPDNP2DKRXMF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OH2ATH2BKDNKCJAU4WPPXK4SHLE3UJUV/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39350.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-rrrv-3w42-pffh
- https://nvd.nist.gov/vuln/detail/CVE-2023-39350
- https://security.gentoo.org/glsa/202401-16
- https://github.com/FreeRDP/FreeRDP/commit/e204fc8be5a372626b13f66daf2abafe71dbc2dc
