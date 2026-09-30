# [H] JLSEC-2026-80

## Summary
Severity: High
Advisory: JLSEC-2026-80
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/JLSEC-2026-80
Type: osv

## Affected
- Julia: `Poppler_jll` — affected >=0 <23.12.0+0

## Details
Xpdf prior to version 4.04 contains an integer overflow in the JBIG2 decoder (JBIG2Stream::readTextRegionSeg() in JBIG2Stream.cc). Processing a specially crafted PDF file or JBIG2 image could lead to a crash or the execution of arbitrary code. This is similar to the vulnerability described by CVE-2021-30860 (Apple CoreGraphics).

## References
- http://www.openwall.com/lists/oss-security/2022/09/02/11
- http://www.xpdfreader.com/security-fixes.html
- https://dl.xpdfreader.com/xpdf-4.04.tar.gz
- https://github.com/jeffssh/CVE-2021-30860
- https://github.com/zmanion/Vulnerabilities/blob/main/CVE-2022-38171.md
- https://googleprojectzero.blogspot.com/2021/12/a-deep-dive-into-nso-zero-click.html
- https://www.cve.org/CVERecord?id=CVE-2021-30860
