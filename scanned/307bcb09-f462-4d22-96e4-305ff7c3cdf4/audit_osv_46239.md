# [H] Poppler before 25.04.0 allows crafted input files to trigger out-of-bounds reads in the...

## Summary
Severity: High
Advisory: JLSEC-2026-86
Ecosystem: Julia
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/JLSEC-2026-86
Type: osv

## Affected
- Julia: `Poppler_jll` — affected >=0 <25.10.0+0

## Details
Poppler before 25.04.0 allows crafted input files to trigger out-of-bounds reads in the JBIG2Bitmap::combine function in JBIG2Stream.cc because of a misplaced isOk check.

## References
- https://github.com/advisories/GHSA-r4rq-7765-p57x
- https://gitlab.freedesktop.org/poppler/poppler/-/issues/1577
- https://gitlab.freedesktop.org/poppler/poppler/-/merge_requests/1792
- https://lists.debian.org/debian-lts-announce/2025/04/msg00037.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-32365
