# [H] libde265 has a heap buffer overflow in de265_image_get_buffer via SPS dimension integer overflow

## Summary
Severity: High
Advisory: CVE-2026-49346
Aliases: GHSA-vv8h-932h-7r86
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-49346
Type: osv

## Details
libde265 is an open source implementation of the h.265 video codec. Prior to version 1.1.0, a crafted H.265 bitstream with large SPS dimensions and 16-bit bit depth causes a signed integer overflow in `de265_image_get_buffer()` (`libde265/image.cc:128`). The overflow wraps the plane allocation size to a small value (~1 KB), but the subsequent `fill_image()` call computes the real size using `size_t`, writing ~4 GB into the undersized heap buffer. Version 1.1.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49346.json
- https://github.com/strukturag/libde265/security/advisories/GHSA-vv8h-932h-7r86
- https://nvd.nist.gov/vuln/detail/CVE-2026-49346
- https://github.com/strukturag/libde265/commit/8a1b5cf212f78e1c77cb46eb5d56e492a9336eb8
