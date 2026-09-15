# [M] CVE-2021-36978

## Summary
Severity: Medium
Advisory: CVE-2021-36978
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-07-20
Source: https://osv.dev/vulnerability/CVE-2021-36978
Type: osv

## Details
QPDF 9.x through 9.1.1 and 10.x through 10.0.4 has a heap-based buffer overflow in Pl_ASCII85Decoder::write (called from Pl_AES_PDF::flush and Pl_AES_PDF::finish) when a certain downstream write fails.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00037.html
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/qpdf/OSV-2020-2245.yaml
- https://security.gentoo.org/glsa/202401-20
- https://github.com/qpdf/qpdf/issues/492
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=28262
- https://github.com/qpdf/qpdf/commit/dc92574c10f3e2516ec6445b88c5d584f40df4e5
