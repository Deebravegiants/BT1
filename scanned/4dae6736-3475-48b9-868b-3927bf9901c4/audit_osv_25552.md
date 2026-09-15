# [M] FreeRDP Out-Of-Bounds Read in nsc_rle_decompress_data

## Summary
Severity: Medium
Advisory: CVE-2023-39354
Aliases: GHSA-c3r2-pxxp-f8r6
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-08-31
Source: https://osv.dev/vulnerability/CVE-2023-39354
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol (RDP), released under the Apache license. Affected versions are subject to an Out-Of-Bounds Read in the `nsc_rle_decompress_data` function. The Out-Of-Bounds Read occurs because it processes `context->Planes` without  checking if it contains data of sufficient length. Should an attacker be able to leverage this vulnerability they may be able to cause a crash. This issue has been addressed in versions 2.11.0 and 3.0.0-beta3. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/A6LLDAPEXRDJOM3PREDDD267SSNT77DP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IHMTGKCZXJPQOR5ZD2I4GPDNP2DKRXMF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OH2ATH2BKDNKCJAU4WPPXK4SHLE3UJUV/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39354.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-c3r2-pxxp-f8r6
- https://nvd.nist.gov/vuln/detail/CVE-2023-39354
- https://security.gentoo.org/glsa/202401-16
- https://github.com/FreeRDP/FreeRDP/commit/cd1da25a87358eb3b5512fd259310e95b19a05ec
