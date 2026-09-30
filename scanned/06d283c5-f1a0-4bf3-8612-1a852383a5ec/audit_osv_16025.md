# [H] CVE-2019-25048

## Summary
Severity: High
Advisory: CVE-2019-25048
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2021-07-01
Source: https://osv.dev/vulnerability/CVE-2019-25048
Type: osv

## Details
LibreSSL 2.9.1 through 3.2.1 has a heap-based buffer over-read in do_print_ex (called from asn1_item_print_ctx and ASN1_item_print).

## References
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/libressl/OSV-2020-1923.yaml
- https://github.com/libressl-portable/portable/commit/17c88164016df821df2dff4b2b1291291ec4f28a
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=13914
