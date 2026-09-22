# [M] CVE-2025-48174

## Summary
Severity: Medium
Advisory: CVE-2025-48174
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:L)
Published: 2025-05-16
Source: https://osv.dev/vulnerability/CVE-2025-48174
Type: osv

## Details
In libavif before 1.3.0, makeRoom in stream.c has an integer overflow and resultant buffer overflow in stream->offset+size.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00031.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48174.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-48174
- https://github.com/AOMediaCodec/libavif/commit/50a743062938a3828581d725facc9c2b92a1d109
- https://github.com/AOMediaCodec/libavif/commit/c9f1bea437f21cb78f9919c332922a3b0ba65e11
- https://github.com/AOMediaCodec/libavif/commit/e5fdefe7d1776e6c4cf1703c163a8c0535599029
- https://github.com/AOMediaCodec/libavif/pull/2768
