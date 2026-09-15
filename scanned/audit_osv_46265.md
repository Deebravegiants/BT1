# [M] JLSEC-2026-897

## Summary
Severity: Medium
Advisory: JLSEC-2026-897
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-897
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+3

## Details
A heap buffer overflow issue was found in ImageMagick. When an application processes a malformed TIFF file, it could lead to undefined behavior or a crash causing a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2022-3213
- https://access.redhat.com/security/cve/CVE-2022-3213
- https://bugzilla.redhat.com/show_bug.cgi?id=2126824
- https://bugzilla.redhat.com/show_bug.cgi?id=2126824
- https://github.com/ImageMagick/ImageMagick/commit/30ccf9a0da1f47161b5935a95be854fe84e6c2a2
- https://github.com/ImageMagick/ImageMagick/commit/30ccf9a0da1f47161b5935a95be854fe84e6c2a2
- https://github.com/ImageMagick/ImageMagick6/commit/1aea203eb36409ce6903b9e41fe7cb70030e8750
- https://github.com/ImageMagick/ImageMagick6/commit/1aea203eb36409ce6903b9e41fe7cb70030e8750
