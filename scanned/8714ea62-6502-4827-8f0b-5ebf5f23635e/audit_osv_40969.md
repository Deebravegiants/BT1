# [C] ImageMagick - Command Injection via SVG Decoder

## Summary
Severity: Critical
Advisory: CVE-2026-56379
Aliases: GHSA-xpg8-7m6m-jf56
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-56379
Type: osv

## Details
ImageMagick before 7.1.2-15 and 6.9.13-40 contains a command injection vulnerability in the SVG decoder that allows attackers to inject arbitrary MVG drawing commands. Attackers can craft malicious SVG files with injected Magick Vector Graphics commands that execute during rendering.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-56379.json
- https://access.redhat.com/errata/RHSA-2026:32961
- https://access.redhat.com/security/cve/CVE-2026-56379
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56379.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-xpg8-7m6m-jf56
- https://nvd.nist.gov/vuln/detail/CVE-2026-56379
- https://www.vulncheck.com/advisories/imagemagick-command-injection-via-svg-decoder
- https://bugzilla.redhat.com/show_bug.cgi?id=2491700
