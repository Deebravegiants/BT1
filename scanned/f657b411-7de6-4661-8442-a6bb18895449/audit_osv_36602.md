# [M] FreeRDP has a heap-use-after-free in audio_format_compatible

## Summary
Severity: Medium
Advisory: CVE-2026-24676
Aliases: GHSA-qh5p-frq4-pgxj
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-24676
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.22.0, AUDIN format renegotiation frees the active format list while the capture thread continues using audin->format, leading to a use after free in audio_format_compatible. This vulnerability is fixed in 3.22.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24676.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-qh5p-frq4-pgxj
- https://nvd.nist.gov/vuln/detail/CVE-2026-24676
- https://github.com/FreeRDP/FreeRDP/commit/026b81ae5831ac1598d8f7371e0d0996fac7db00
