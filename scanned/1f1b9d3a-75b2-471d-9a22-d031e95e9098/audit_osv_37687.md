# [M] libheif is Vulnerable to Infinite Loop DoS via stts Sample Duration Lookup

## Summary
Severity: Medium
Advisory: CVE-2026-32739
Aliases: GHSA-j9g7-q9hv-gq8c
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-32739
Type: osv

## Details
libheif is a HEIF and AVIF file format decoder and encoder. In versions 1.21.2 and below, a crafted 800-byte HEIF sequence file causes an infinite loop in Box_stts::get_sample_duration(), consuming 100% CPU indefinitely with zero progress, leading to DoS. The loop has no iteration limit or timeout and is triggered during file open (parsing) - before any user interaction or image decoding. The process stays alive (no crash, no error logged), making it invisible to crash-based monitoring. This issue has been fixed in version 1.22.0.

## References
- https://github.com/strukturag/libheif/releases/tag/v1.22.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32739.json
- https://github.com/strukturag/libheif/security/advisories/GHSA-j9g7-q9hv-gq8c
- https://nvd.nist.gov/vuln/detail/CVE-2026-32739
