# [H] libwebp: OOB write in BuildHuffmanTable

## Summary
Severity: High
Advisory: GHSA-j7hp-h8jx-5ppr
CVE: CVE-2023-4863
CWE: CWE-787
Ecosystem: Go, NuGet, PyPI, crates.io, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-12
Source: https://github.com/advisories/GHSA-j7hp-h8jx-5ppr
Type: github-advisory

## Affected
- crates.io: `libwebp-sys2` — affected >=0 <0.1.8
- crates.io: `libwebp-sys` — affected >=0 <0.9.3
- npm: `electron` — affected >=22.0.0 <22.3.24
- npm: `electron` — affected >=24.0.0 <24.8.3
- npm: `electron` — affected >=25.0.0 <25.8.1
- npm: `electron` — affected >=26.0.0 <26.2.1
- npm: `electron` — affected >=27.0.0-beta.1 <27.0.0-beta.2
- NuGet: `SkiaSharp` — affected >=2.0.0 <2.88.6
- Go: `github.com/chai2010/webp` — affected >=1.1.2 <1.4.0
- PyPI: `Pillow` — affected >=0 <10.0.1
- crates.io: `webp` — affected >=0 <0.2.6
- NuGet: `magick.net-q16-anycpu` — affected >=0 <13.3.0
- NuGet: `magick.net-q16-hdri-anycpu` — affected >=0 <13.3.0
- NuGet: `magick.net-q16-x64` — affected >=0 <13.3.0
- NuGet: `magick.net-q8-anycpu` — affected >=0 <13.3.0
- NuGet: `magick.net-q8-openmp-x64` — affected >=0 <13.3.0
- NuGet: `magick.net-q8-x64` — affected >=0 <13.3.0
- Go: `github.com/chai2010/webp` — affected >=0 <0.0.0-20250406010349-76805d5a8860
- Go: `github.com/chai2010/webp` — affected >=0.0.0 <1.1.2-0.20250406010349-76805d5a8860

## Details
Heap buffer overflow in libwebp allow a remote attacker to perform an out of bounds memory write via a crafted HTML page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4863
- https://github.com/qnighy/libwebp-sys2-rs/pull/21
- https://github.com/python-pillow/Pillow/pull/7395
- https://github.com/jaredforth/webp/pull/30
- https://github.com/electron/electron/pull/39823
- https://github.com/electron/electron/pull/39825
- https://github.com/electron/electron/pull/39826
- https://github.com/electron/electron/pull/39827
- https://github.com/electron/electron/pull/39828
- https://github.com/webmproject/libwebp/commit/902bc9190331343b2017211debcec8d2ab87e17a
- https://github.com/qnighy/libwebp-sys2-rs/commit/4560c473a76ec8bd8c650f19ddf9d7a44f719f8b
- https://github.com/jaredforth/webp/commit/9d4c56e63abecc777df71c702503c3eaabd7dcbc
- https://security.gentoo.org/glsa/202401-10
- https://security.gentoo.org/glsa/202309-05
- https://security-tracker.debian.org/tracker/CVE-2023-4863
- https://rustsec.org/advisories/RUSTSEC-2023-0061.html
- https://rustsec.org/advisories/RUSTSEC-2023-0060.html
- https://pillow.readthedocs.io/en/stable/releasenotes/10.0.1.html#security
- https://news.ycombinator.com/item?id=37478403
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2023-4863
