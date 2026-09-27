# [H] JLSEC-2026-998

## Summary
Severity: High
Advisory: JLSEC-2026-998
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-998
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. In versions below both 7.1.2-19 and 6.9.13-44, Magick frees the memory of the XML tree via the `DestroyXMLTree()` function; however, this process is executed recursively with no depth limit imposed. When Magick processes an XML file with deeply nested structures, it will exhaust the stack memory, resulting in a Denial of Service (DoS) attack. This issue has been fixed in versions 6.9.13-44 and 7.1.2-19.

## References
- https://access.redhat.com/security/cve/CVE-2026-33908
- https://bugzilla.redhat.com/show_bug.cgi?id=2458041
- https://github.com/ImageMagick/ImageMagick/commit/ccdc01180276aa2cb3d4a32a611aa4f417061cd8
- https://github.com/ImageMagick/ImageMagick/releases/tag/7.1.2-19
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-fwvm-ggf6-2p4x
- https://github.com/dlemstra/Magick.NET/releases/tag/14.12.0
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33908.json
