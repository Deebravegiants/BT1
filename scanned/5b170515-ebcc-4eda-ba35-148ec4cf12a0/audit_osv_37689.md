# [H] libheif has a heap buffer overflow in decode_mask_image()

## Summary
Severity: High
Advisory: CVE-2026-32741
Aliases: GHSA-j3w5-7whq-p37q
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-32741
Type: osv

## Details
libheif is a HEIF and AVIF file format decoder and encoder. Versions 1.21.2 and below contain a heap buffer overflow in MaskImageCodec::decode_mask_image(). When decoding a HEIF file containing a mask image (mski), the function copies the full iloc extent data into a pixel buffer using memcpy(dst, data.data(), data.size()). The copy length data.size() is determined by the iloc extent in the file (attacker-controlled), while the destination buffer is sized based on the declared image dimensions. Because no upper-bound check exists on the data length, a crafted file whose iloc extent exceeds the pixel buffer allocation overflows the heap. The vulnerable single-memcpy branch is reached when the mskC property specifies bits_per_pixel = 8 and the ispe property declares an even width ≥ 64 (so that stride == width), with no changes to default security limits or external codec plugins required. This issue has been fixed in version 1.22.0.

## References
- https://github.com/strukturag/libheif/releases/tag/v1.22.0
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-32741.json
- https://access.redhat.com/security/cve/CVE-2026-32741
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32741.json
- https://github.com/strukturag/libheif/security/advisories/GHSA-j3w5-7whq-p37q
- https://nvd.nist.gov/vuln/detail/CVE-2026-32741
- https://bugzilla.redhat.com/show_bug.cgi?id=2480002
