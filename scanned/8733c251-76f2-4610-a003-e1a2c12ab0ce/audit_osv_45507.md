# [C] In libavif before 1.3.0, makeRoom in stream.c has an integer overflow and resultant buffer overflow...

## Summary
Severity: Critical
Advisory: JLSEC-2026-125
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-125
Type: osv

## Affected
- Julia: `libavif_jll` — affected >=0 <1.3.0+0

## Details
In libavif before 1.3.0, makeRoom in stream.c has an integer overflow and resultant buffer overflow in stream->offset+size.

## References
- https://github.com/AOMediaCodec/libavif/commit/50a743062938a3828581d725facc9c2b92a1d109
- https://github.com/AOMediaCodec/libavif/commit/c9f1bea437f21cb78f9919c332922a3b0ba65e11
- https://github.com/AOMediaCodec/libavif/commit/e5fdefe7d1776e6c4cf1703c163a8c0535599029
- https://github.com/AOMediaCodec/libavif/pull/2768
- https://github.com/advisories/GHSA-f6x7-5x3c-j3rg
- https://lists.debian.org/debian-lts-announce/2025/05/msg00031.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-48174
