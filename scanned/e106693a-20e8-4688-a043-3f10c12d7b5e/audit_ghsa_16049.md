# [M] TCPDF Local File Inclusion vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rmv2-8jjc-23xw
CVE: CVE-2024-51058
CWE: CWE-552
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-26
Source: https://github.com/advisories/GHSA-rmv2-8jjc-23xw
Type: github-advisory

## Affected
- Packagist: `tecnickcom/tcpdf` — affected >=0 <6.7.6

## Details
Local File Inclusion (LFI) vulnerability has been discovered in TCPDF 6.7.5. This vulnerability enables a user to read arbitrary files from the server's file system through <img> src tag, potentially exposing sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-51058
- https://github.com/tecnickcom/TCPDF/commit/bfa7d2b6d455ebf72ebe3d48fbd487ee5a1f6f3b
- https://github.com/saravana-hackz/vulnerability-research/tree/main/CVE-2024-51058
- https://github.com/tecnickcom/TCPDF
- https://lists.debian.org/debian-lts-announce/2025/06/msg00004.html
