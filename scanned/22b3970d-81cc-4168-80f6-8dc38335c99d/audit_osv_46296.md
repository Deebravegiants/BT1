# [H] JLSEC-2026-979

## Summary
Severity: High
Advisory: JLSEC-2026-979
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-979
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 7.1.2-16 and 6.9.13-41, an uninitialized pointer dereference vulnerability exists in the JBIG decoder due to a missing check. This vulnerability is fixed in 7.1.2-16 and 6.9.13-41.

## References
- https://access.redhat.com/errata/RHSA-2026:6713
- https://access.redhat.com/security/cve/CVE-2026-28691
- https://bugzilla.redhat.com/show_bug.cgi?id=2445902
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-wj8w-pjxf-9g4f
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-28691.json
