# [H] ImageMagick: Infinite Loop in the MIFF decoder can lead to CPU exhaustion

## Summary
Severity: High
Advisory: CVE-2026-46522
Aliases: GHSA-7gg8-qqx7-92g5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-46522
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 7.1.2.23 and 6.9.13-48, due to a missing check in the MIFF decoder, a crafted file could cause an infinite loop resulting in CPU exhaustion. Versions 7.1.2.23 and 6.9.13-48 fix the issue.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46522.json
- https://access.redhat.com/errata/RHSA-2026:32961
- https://access.redhat.com/security/cve/CVE-2026-46522
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46522.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-7gg8-qqx7-92g5
- https://nvd.nist.gov/vuln/detail/CVE-2026-46522
- https://bugzilla.redhat.com/show_bug.cgi?id=2487730
