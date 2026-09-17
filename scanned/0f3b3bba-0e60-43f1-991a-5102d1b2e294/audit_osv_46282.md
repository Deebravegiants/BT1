# [M] In multispectral MIFF image processing in ImageMagick before 7.1.1-44, packet_size is mishandled ...

## Summary
Severity: Medium
Advisory: JLSEC-2026-915
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-915
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.1047+0

## Details
In multispectral MIFF image processing in ImageMagick before 7.1.1-44, `packet_size` is mishandled (related to the rendering of all channels in an arbitrary order).

## References
- https://github.com/ImageMagick/ImageMagick/commit/81ac8a0d2eb21739842ed18c48c7646b7eef65b8
- https://github.com/ImageMagick/Website/blob/main/ChangeLog.md#711-44---2025-02-22
- https://github.com/advisories/GHSA-f57x-prr8-55vv
- https://nvd.nist.gov/vuln/detail/CVE-2025-46393
