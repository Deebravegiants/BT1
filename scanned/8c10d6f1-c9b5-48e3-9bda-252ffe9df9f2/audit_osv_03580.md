# [M] ALPINE-CVE-2026-32739

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-32739
Ecosystem: Alpine:v3.23
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-32739
Type: osv

## Affected
- Alpine:v3.23: `libheif` — affected >=0 <1.23.0-r0

## Details
libheif is a HEIF and AVIF file format decoder and encoder. In versions 1.21.2 and below, a crafted 800-byte HEIF sequence file causes an infinite loop in Box_stts::get_sample_duration(), consuming 100% CPU indefinitely with zero progress, leading to DoS. The loop has no iteration limit or timeout and is triggered during file open (parsing) - before any user interaction or image decoding. The process stays alive (no crash, no error logged), making it invisible to crash-based monitoring. This issue has been fixed in version 1.22.0.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-32739
