# [M] nghttp2 is an implementation of the Hypertext Transfer Protocol version 2 in C

## Summary
Severity: Medium
Advisory: JLSEC-2026-4
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-23
Source: https://osv.dev/vulnerability/JLSEC-2026-4
Type: osv

## Affected
- Julia: `nghttp2_jll` — affected >=0 <1.61.0+0

## Details
nghttp2 is an implementation of the Hypertext Transfer Protocol version 2 in C. The nghttp2 library prior to version 1.61.0 keeps reading the unbounded number of HTTP/2 CONTINUATION frames even after a stream is reset to keep HPACK context in sync.  This causes excessive CPU usage to decode HPACK stream. nghttp2 v1.61.0 mitigates this vulnerability by limiting the number of CONTINUATION frames it accepts per stream. There is no workaround for this vulnerability.

## References
- http://www.openwall.com/lists/oss-security/2024/04/03/16
- https://github.com/nghttp2/nghttp2/commit/00201ecd8f982da3b67d4f6868af72a1b03b14e0
- https://github.com/nghttp2/nghttp2/commit/d71a4668c6bead55805d18810d633fbb98315af9
- https://github.com/nghttp2/nghttp2/security/advisories/GHSA-x6x3-gv8h-m57q
- https://lists.debian.org/debian-lts-announce/2024/04/msg00026.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00041.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AGOME6ZXJG7664IPQNVE3DL67E3YP3HY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/J6ZMXUGB66VAXDW5J6QSTHM5ET25FGSA/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PXJO2EASHM2OQQLGVDY5ZSO7UVDVHTDK/
- https://www.kb.cert.org/vuls/id/421644
