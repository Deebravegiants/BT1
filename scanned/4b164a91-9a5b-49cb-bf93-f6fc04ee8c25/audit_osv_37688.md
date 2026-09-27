# [H] libheif: Heap-Buffer-Overflow Write in Grid Tile Chroma Compositing

## Summary
Severity: High
Advisory: CVE-2026-32740
Aliases: GHSA-frfr-f3vg-2g6j
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-32740
Type: osv

## Details
libheif is a HEIF and AVIF file format decoder and encoder. Versions 1.21.2 and prior contain a heap-buffer-overflow (write) vulnerability in the grid tile compositing, allowing an attacker to write 64 bytes of fully attacker-controlled data past the end of a chroma plane heap allocation by crafting a HEIF/AVIF file with a 1×4 grid of odd-height tiles. The overflow is triggered during normal image decoding with default build configuration. The written bytes are chroma (Cb/Cr) pixel values from the attacking tile, giving the attacker full control over the overflow content. This issue has been fixed in version 1.22.0.

## References
- https://github.com/strukturag/libheif/releases/tag/v1.22.0
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-32740.json
- https://access.redhat.com/security/cve/CVE-2026-32740
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32740.json
- https://github.com/strukturag/libheif/security/advisories/GHSA-frfr-f3vg-2g6j
- https://nvd.nist.gov/vuln/detail/CVE-2026-32740
- https://bugzilla.redhat.com/show_bug.cgi?id=2479969
