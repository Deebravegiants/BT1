# [M] JLSEC-2026-905

## Summary
Severity: Medium
Advisory: JLSEC-2026-905
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-905
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.1+0

## Details
A vulnerability was found in ImageMagick. This security flaw ouccers as an undefined behaviors of casting double to `size_t` in svg, mvg and other coders (recurring bugs of CVE-2022-32546).

## References
- https://access.redhat.com/security/cve/CVE-2023-34151
- https://access.redhat.com/security/cve/CVE-2023-34151
- https://bugzilla.redhat.com/show_bug.cgi?id=2210657
- https://bugzilla.redhat.com/show_bug.cgi?id=2210657
- https://github.com/ImageMagick/ImageMagick/issues/6341
- https://github.com/ImageMagick/ImageMagick/issues/6341
- https://lists.debian.org/debian-lts-announce/2024/02/msg00007.html
- https://lists.debian.org/debian-lts-announce/2024/02/msg00007.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4UFQJCYJ23HWHNDOVKBHZQ7HCXXL6MM3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4UFQJCYJ23HWHNDOVKBHZQ7HCXXL6MM3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/V2ZUHZXQ2C3JZYKPW4XHCMVVL467MA2V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/V2ZUHZXQ2C3JZYKPW4XHCMVVL467MA2V/
