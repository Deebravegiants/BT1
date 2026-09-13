# [H] JLSEC-2026-481

## Summary
Severity: High
Advisory: JLSEC-2026-481
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-481
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.1.0+0

## Details
Buffer Overflow in LibTiff v4.0.10 allows attackers to cause a denial of service via the "invertImage()" function in the component "tiffcrop".

## References
- http://blog.topsec.com.cn/%E5%A4%A9%E8%9E%8D%E4%BF%A1%E5%85%B3%E4%BA%8Elibtiff%E4%B8%ADinvertimage%E5%87%BD%E6%95%B0%E5%A0%86%E6%BA%A2%E5%87%BA%E6%BC%8F%E6%B4%9E%E7%9A%84%E5%88%86%E6%9E%90/
- http://bugzilla.maptools.org/show_bug.cgi?id=2831
- https://lists.debian.org/debian-lts-announce/2021/10/msg00004.html
