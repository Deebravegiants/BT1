# [M] JLSEC-2026-210

## Summary
Severity: Medium
Advisory: JLSEC-2026-210
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-210
Type: osv

## Affected
- Julia: `Leptonica_jll` — affected >=0 <1.81.1+0

## Details
An issue in the Leptonica linked library (v1.79.0) allows attackers to cause an arithmetic exception leading to a Denial of Service (DoS) via a crafted JPEG file.

## References
- https://github.com/DanBloomberg/leptonica/commit/f062b42c0ea8dddebdc6a152fd16152de215d614
- https://github.com/tesseract-ocr/tesseract/issues/3498
- https://lists.debian.org/debian-lts-announce/2022/12/msg00018.html
- https://security.gentoo.org/glsa/202312-01
