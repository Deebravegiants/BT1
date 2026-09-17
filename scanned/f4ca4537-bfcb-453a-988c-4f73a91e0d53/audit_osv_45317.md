# [M] In libxml2 before 2.9.14, several buffer handling functions in buf.c (`xmlBuf*`) and tree.c...

## Summary
Severity: Medium
Advisory: JLSEC-2025-75
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/JLSEC-2025-75
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=0 <2.9.14+0
- Julia: `XSLT_jll` — affected >=0 <1.1.41+0

## Details
In libxml2 before 2.9.14, several buffer handling functions in buf.c (`xmlBuf*`) and tree.c (`xmlBuffer*`) don't check for integer overflows. This can result in out-of-bounds memory writes. Exploitation requires a victim to open a crafted, multi-gigabyte XML file. Other software using libxml2's buffer functions, for example libxslt through 1.1.35, is affected as well.

## References
- http://packetstormsecurity.com/files/167345/libxml2-xmlBufAdd-Heap-Buffer-Overflow.html
- http://packetstormsecurity.com/files/169825/libxml2-xmlParseNameComplex-Integer-Overflow.html
- https://gitlab.gnome.org/GNOME/libxml2/-/commit/2554a2408e09f13652049e5ffb0d26196b02ebab
- https://gitlab.gnome.org/GNOME/libxml2/-/commit/6c283d83eccd940bcde15634ac8c7f100e3caefd
- https://gitlab.gnome.org/GNOME/libxml2/-/tags/v2.9.14
- https://gitlab.gnome.org/GNOME/libxslt/-/tags
- https://lists.debian.org/debian-lts-announce/2022/05/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FZOBT5Y6Y2QLDDX2HZGMV7MJMWGXORKK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/P3NVZVWFRBXBI3AKZZWUWY6INQQPQVSF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/P5363EDV5VHZ5C77ODA43RYDCPMA7ARM/
- https://security.gentoo.org/glsa/202210-03
- https://security.netapp.com/advisory/ntap-20220715-0006/
- https://www.debian.org/security/2022/dsa-5142
- https://www.oracle.com/security-alerts/cpujul2022.html
