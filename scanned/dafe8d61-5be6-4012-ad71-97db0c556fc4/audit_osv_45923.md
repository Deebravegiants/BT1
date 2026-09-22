# [C] JLSEC-2026-479

## Summary
Severity: Critical
Advisory: JLSEC-2026-479
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-479
Type: osv

## Affected
- Julia: `GCCBootstrap_jll` — affected unspecified
- Julia: `Openresty_jll` — affected >=0 <1.27.1+0
- Julia: `Zlib_jll` — affected >=0 <1.3.1+0

## Details
MiniZip in zlib through 1.3 has an integer overflow and resultant heap-based buffer overflow in `zipOpenNewFileInZip4_64` via a long filename, comment, or extra field. NOTE: MiniZip is not a supported part of the zlib product. NOTE: pyminizip through 0.2.6 is also vulnerable because it bundles an affected zlib version, and exposes the applicable MiniZip code through its compress API.

## References
- http://www.openwall.com/lists/oss-security/2023/10/20/9
- http://www.openwall.com/lists/oss-security/2024/01/24/10
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://cert-portal.siemens.com/productcert/html/ssa-470355.html
- https://cert-portal.siemens.com/productcert/html/ssa-769027.html
- https://chromium.googlesource.com/chromium/src/+/d709fb23806858847131027da95ef4c548813356
- https://chromium.googlesource.com/chromium/src/+/de29dd6c7151d3cd37cb4cf0036800ddfb1d8b61
- https://github.com/madler/zlib/blob/ac8f12c97d1afd9bafa9c710f827d40a407d3266/contrib/README.contrib#L1-L4
- https://github.com/madler/zlib/pull/843
- https://lists.debian.org/debian-lts-announce/2023/11/msg00026.html
- https://pypi.org/project/pyminizip/#history
- https://security.gentoo.org/glsa/202401-18
- https://security.netapp.com/advisory/ntap-20231130-0009/
- https://www.winimage.com/zLibDll/minizip.html
