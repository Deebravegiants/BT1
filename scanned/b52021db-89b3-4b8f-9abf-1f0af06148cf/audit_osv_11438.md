# [M] CVE-2017-7854

## Summary
Severity: Medium
Advisory: CVE-2017-7854
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-13
Source: https://osv.dev/vulnerability/CVE-2017-7854
Type: osv

## Details
The consume_init_expr function in wasm.c in radare2 1.3.0 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted Web Assembly file.

## References
- http://www.securityfocus.com/bid/97648
- https://github.com/radare/radare2/commit/d2632f6483a3ceb5d8e0a5fb11142c51c43978b4
- https://github.com/radare/radare2/issues/7265
