# [M] JLSEC-2026-910

## Summary
Severity: Medium
Advisory: JLSEC-2026-910
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-910
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.1+0

## Details
A heap use after free issue was discovered in ImageMagick's ReplaceXmpValue() function in `MagickCore/profile.c`. An attacker could trick user to open a specially crafted file to convert, triggering an heap-use-after-free write error, allowing an application to crash, resulting in a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2023-34475
- https://access.redhat.com/security/cve/CVE-2023-34475
- https://bugzilla.redhat.com/show_bug.cgi?id=2214149
- https://bugzilla.redhat.com/show_bug.cgi?id=2214149
- https://github.com/ImageMagick/ImageMagick/commit/1061db7f80fdc9ef572ac60b55f408f7bab6e1b0
- https://github.com/ImageMagick/ImageMagick/commit/1061db7f80fdc9ef572ac60b55f408f7bab6e1b0
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/45DUUXYMAEEAW55GSLAXN25VPKCRAIDA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/45DUUXYMAEEAW55GSLAXN25VPKCRAIDA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4UFQJCYJ23HWHNDOVKBHZQ7HCXXL6MM3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4UFQJCYJ23HWHNDOVKBHZQ7HCXXL6MM3/
