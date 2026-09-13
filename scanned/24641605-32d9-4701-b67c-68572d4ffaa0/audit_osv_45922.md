# [C] JLSEC-2026-478

## Summary
Severity: Critical
Advisory: JLSEC-2026-478
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-478
Type: osv

## Affected
- Julia: `GCCBootstrap_jll` — affected unspecified
- Julia: `Openresty_jll` — affected >=0 <1.27.1+0
- Julia: `Zlib_jll` — affected >=0 <1.2.13+0

## Details
zlib through 1.2.12 has a heap-based buffer over-read or buffer overflow in inflate in inflate.c via a large gzip header extra field. NOTE: only applications that call inflateGetHeader are affected. Some common applications bundle the affected zlib source code but may be unable to call inflateGetHeader (e.g., see the nodejs/node reference).

## References
- http://seclists.org/fulldisclosure/2022/Oct/37
- http://seclists.org/fulldisclosure/2022/Oct/38
- http://seclists.org/fulldisclosure/2022/Oct/41
- http://seclists.org/fulldisclosure/2022/Oct/42
- http://www.openwall.com/lists/oss-security/2022/08/05/2
- http://www.openwall.com/lists/oss-security/2022/08/09/1
- https://cert-portal.siemens.com/productcert/html/ssa-150063.html
- https://cert-portal.siemens.com/productcert/html/ssa-202008.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://cert-portal.siemens.com/productcert/html/ssa-470355.html
- https://cert-portal.siemens.com/productcert/html/ssa-561322.html
- https://github.com/curl/curl/issues/9271
- https://github.com/ivd38/zlib_overflow
- https://github.com/madler/zlib/blob/21767c654d31d2dccdde4330529775c6c5fd5389/zlib.h#L1062-L1063
- https://github.com/madler/zlib/commit/1eb7682f845ac9e9bf9ae35bbfb3bad5dacbd91d
- https://github.com/madler/zlib/commit/eff308af425b67093bab25f80f1ae950166bece1
- https://github.com/nodejs/node/blob/75b68c6e4db515f76df73af476eccf382bbcb00a/deps/zlib/inflate.c#L762-L764
- https://lists.debian.org/debian-lts-announce/2022/09/msg00012.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JWN4VE3JQR4O2SOUS5TXNLANRPMHWV4I/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NMBOJ77A7T7PQCARMDUK75TE6LLESZ3O/
