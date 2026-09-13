# [H] ImageMagick: Heap Buffer Over-Write in IPL decoder when reading multiple images of different dimensions

## Summary
Severity: High
Advisory: CVE-2026-46520
Aliases: GHSA-36wm-hprc-mcf5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-46520
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 6.9.13-48 and 7.1.2-23, when reading multiple images with different dimensions an out of bounds heap write can occur. This issue has been patched in versions 6.9.13-48 and 7.1.2-23.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46520.json
- https://access.redhat.com/errata/RHSA-2026:32961
- https://access.redhat.com/security/cve/CVE-2026-46520
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46520.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-36wm-hprc-mcf5
- https://nvd.nist.gov/vuln/detail/CVE-2026-46520
- https://bugzilla.redhat.com/show_bug.cgi?id=2487729
