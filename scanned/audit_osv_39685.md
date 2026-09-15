# [M] ImageMagick: Use-After-Free in MSL decoder.

## Summary
Severity: Medium
Advisory: CVE-2026-46523
Aliases: GHSA-5r4x-w6p5-222q
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-46523
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 7.1.2.23 and 6.9.13-48, a crafted MSL image can trigger a heap-use-after-free. Versions 7.1.2.23 and 6.9.13-48 fix the issue.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46523.json
- https://access.redhat.com/errata/RHSA-2026:32961
- https://access.redhat.com/security/cve/CVE-2026-46523
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46523.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-5r4x-w6p5-222q
- https://nvd.nist.gov/vuln/detail/CVE-2026-46523
- https://bugzilla.redhat.com/show_bug.cgi?id=2487743
