# [H] ImageMagick: Out-of-bounds write in ICON decoder due to incorrect loop

## Summary
Severity: High
Advisory: CVE-2026-53461
Aliases: GHSA-g22q-f7gc-5jhr
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-53461
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 6.9.13-50 and 7.1.2-25, an incorrect loop in the ICON decoder can result in an out of bounds heap write resulting in a crash. This issue has been patched in versions 6.9.13-50 and 7.1.2-25.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53461.json
- https://access.redhat.com/security/cve/CVE-2026-53461
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53461.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-g22q-f7gc-5jhr
- https://nvd.nist.gov/vuln/detail/CVE-2026-53461
- https://bugzilla.redhat.com/show_bug.cgi?id=2487764
