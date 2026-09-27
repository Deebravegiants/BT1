# [M] JLSEC-2026-904

## Summary
Severity: Medium
Advisory: JLSEC-2026-904
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-904
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+1

## Details
A stack-based buffer overflow issue was found in ImageMagick's `coders/tiff.c`. This flaw allows an attacker to trick the user into opening a specially crafted malicious tiff file, causing an application to crash, resulting in a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2023-3195
- https://access.redhat.com/security/cve/CVE-2023-3195
- https://bugzilla.redhat.com/show_bug.cgi?id=2214141
- https://bugzilla.redhat.com/show_bug.cgi?id=2214141
- https://github.com/ImageMagick/ImageMagick/commit/f620340935777b28fa3f7b0ed7ed6bd86946934c
- https://github.com/ImageMagick/ImageMagick/commit/f620340935777b28fa3f7b0ed7ed6bd86946934c
- https://github.com/ImageMagick/ImageMagick6/commit/85a370c79afeb45a97842b0959366af5236e9023
- https://github.com/ImageMagick/ImageMagick6/commit/85a370c79afeb45a97842b0959366af5236e9023
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/45DUUXYMAEEAW55GSLAXN25VPKCRAIDA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/45DUUXYMAEEAW55GSLAXN25VPKCRAIDA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4UFQJCYJ23HWHNDOVKBHZQ7HCXXL6MM3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4UFQJCYJ23HWHNDOVKBHZQ7HCXXL6MM3/
- https://www.openwall.com/lists/oss-security/2023/05/29/1
- https://www.openwall.com/lists/oss-security/2023/05/29/1
