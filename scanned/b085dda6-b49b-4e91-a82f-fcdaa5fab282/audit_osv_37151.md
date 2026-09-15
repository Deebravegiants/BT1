# [H] ImageMagick has an integer overflow in DIB coder can result in out of bounds read or write

## Summary
Severity: High
Advisory: CVE-2026-28693
Aliases: GHSA-hffp-q43q-qq76
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-09
Source: https://osv.dev/vulnerability/CVE-2026-28693
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 7.1.2-16 and 6.9.13-41, an integer overflow in DIB coder can result in out of bounds read or write. This vulnerability is fixed in 7.1.2-16 and 6.9.13-41.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-28693.json
- https://access.redhat.com/errata/RHSA-2026:6713
- https://access.redhat.com/security/cve/CVE-2026-28693
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28693.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-hffp-q43q-qq76
- https://nvd.nist.gov/vuln/detail/CVE-2026-28693
- https://bugzilla.redhat.com/show_bug.cgi?id=2445888
