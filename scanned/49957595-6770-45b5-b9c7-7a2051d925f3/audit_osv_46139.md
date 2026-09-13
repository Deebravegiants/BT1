# [M] Heap out-of-bounds read in PKCS7 parsing

## Summary
Severity: Medium
Advisory: JLSEC-2026-720
Ecosystem: Julia
CVSS: 5.4 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-720
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
Heap out-of-bounds read in PKCS7 parsing. A crafted PKCS7 message can trigger an OOB read on the heap. The missing bounds check is in the indefinite-length end-of-content verification loop in `PKCS7_VerifySignedData()`.

## References
- https://github.com/advisories/GHSA-52wm-3mqv-vmmj
- https://github.com/wolfssl/wolfssl/pull/10039
- https://nvd.nist.gov/vuln/detail/CVE-2026-5392
