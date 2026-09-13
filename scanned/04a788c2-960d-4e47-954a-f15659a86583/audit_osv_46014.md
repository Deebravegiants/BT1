# [H] JLSEC-2026-572

## Summary
Severity: High
Advisory: JLSEC-2026-572
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/JLSEC-2026-572
Type: osv

## Affected
- Julia: `libheif_jll` — affected >=0 <1.22.2000+0

## Details
libheif is a HEIF and AVIF file format decoder and encoder. Versions 1.21.2 and prior contain a heap-buffer-overflow (write) vulnerability in the grid tile compositing, allowing an attacker to write 64 bytes of fully attacker-controlled data past the end of a chroma plane heap allocation by crafting a HEIF/AVIF file with a 1×4 grid of odd-height tiles. The overflow is triggered during normal image decoding with default build configuration. The written bytes are chroma (Cb/Cr) pixel values from the attacking tile, giving the attacker full control over the overflow content. This issue has been fixed in version 1.22.0.

## References
- https://access.redhat.com/security/cve/CVE-2026-32740
- https://bugzilla.redhat.com/show_bug.cgi?id=2479969
- https://github.com/strukturag/libheif/releases/tag/v1.22.0
- https://github.com/strukturag/libheif/security/advisories/GHSA-frfr-f3vg-2g6j
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-32740.json
