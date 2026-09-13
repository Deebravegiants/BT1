# [H] ImageMagick has an uninitialized pointer dereference in JBIG decoder

## Summary
Severity: High
Advisory: CVE-2026-28691
Aliases: GHSA-wj8w-pjxf-9g4f
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-09
Source: https://osv.dev/vulnerability/CVE-2026-28691
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 7.1.2-16 and 6.9.13-41, an uninitialized pointer dereference vulnerability exists in the JBIG decoder due to a missing check. This vulnerability is fixed in 7.1.2-16 and 6.9.13-41.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-28691.json
- https://access.redhat.com/errata/RHSA-2026:6713
- https://access.redhat.com/security/cve/CVE-2026-28691
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28691.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-wj8w-pjxf-9g4f
- https://nvd.nist.gov/vuln/detail/CVE-2026-28691
- https://bugzilla.redhat.com/show_bug.cgi?id=2445902
