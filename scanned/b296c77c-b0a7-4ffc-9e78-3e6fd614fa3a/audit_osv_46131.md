# [C] Stack Buffer Overflow in `wc_HpkeLabeledExtract` via Oversized ECH Config

## Summary
Severity: Critical
Advisory: JLSEC-2026-711
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-711
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.7.2+0 <5.9.2+0

## Details
Stack Buffer Overflow in `wc_HpkeLabeledExtract` via Oversized ECH Config. A vulnerability existed in wolfSSL 5.8.4 ECH (Encrypted Client Hello) support, where a maliciously crafted ECH config could cause a stack buffer overflow on the client side, leading to potential remote execution and client program crash. This could be exploited by a malicious TLS server supporting ECH. Note that ECH is off by default, and is only enabled with enable-ech.

## References
- https://github.com/advisories/GHSA-267h-vrw9-53p3
- https://github.com/wolfSSL/wolfssl/pull/9737
- https://nvd.nist.gov/vuln/detail/CVE-2026-3849
