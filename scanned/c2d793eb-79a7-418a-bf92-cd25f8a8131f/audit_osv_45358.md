# [C] ImageMagick before 7.1.2-15 and 6.9.13-40 contains a command injection vulnerability in the SVG...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1060
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1060
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick before 7.1.2-15 and 6.9.13-40 contains a command injection vulnerability in the SVG decoder that allows attackers to inject arbitrary MVG drawing commands. Attackers can craft malicious SVG files with injected Magick Vector Graphics commands that execute during rendering.

## References
- https://access.redhat.com/errata/RHSA-2026:32961
- https://access.redhat.com/security/cve/CVE-2026-56379
- https://bugzilla.redhat.com/show_bug.cgi?id=2491700
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-xpg8-7m6m-jf56
- https://github.com/advisories/GHSA-v772-658q-978p
- https://nvd.nist.gov/vuln/detail/CVE-2026-56379
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-56379.json
- https://www.vulncheck.com/advisories/imagemagick-command-injection-via-svg-decoder
