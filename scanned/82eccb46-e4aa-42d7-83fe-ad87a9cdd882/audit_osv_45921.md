# [H] JLSEC-2026-477

## Summary
Severity: High
Advisory: JLSEC-2026-477
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-477
Type: osv

## Affected
- Julia: `GCCBootstrap_jll` — affected unspecified
- Julia: `Openresty_jll` — affected >=0 <1.21.4+0
- Julia: `Python_jll` — affected >=0 <3.10.14+0
- Julia: `Zlib_jll` — affected >=0 <1.2.12+3

## Details
zlib before 1.2.12 allows memory corruption when deflating (i.e., when compressing) if the input has many distant matches.

## References
- http://seclists.org/fulldisclosure/2022/May/33
- http://seclists.org/fulldisclosure/2022/May/35
- http://seclists.org/fulldisclosure/2022/May/38
- http://www.openwall.com/lists/oss-security/2022/03/25/2
- http://www.openwall.com/lists/oss-security/2022/03/26/1
- https://cert-portal.siemens.com/productcert/html/ssa-333517.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://cert-portal.siemens.com/productcert/html/ssa-419740.html
- https://cert-portal.siemens.com/productcert/html/ssa-470355.html
- https://cert-portal.siemens.com/productcert/html/ssa-565386.html
- https://cert-portal.siemens.com/productcert/html/ssa-942865.html
- https://cert-portal.siemens.com/productcert/pdf/ssa-333517.pdf
- https://github.com/madler/zlib/commit/5c44459c3b28a9bd3283aaceab7c615f8020c531
- https://github.com/madler/zlib/compare/v1.2.11...v1.2.12
- https://github.com/madler/zlib/issues/605
- https://lists.debian.org/debian-lts-announce/2022/04/msg00000.html
- https://lists.debian.org/debian-lts-announce/2022/05/msg00008.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DCZFIJBJTZ7CL5QXBFKTQ22Q26VINRUF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DF62MVMH3QUGMBDCB3DY2ERQ6EBHTADB/
