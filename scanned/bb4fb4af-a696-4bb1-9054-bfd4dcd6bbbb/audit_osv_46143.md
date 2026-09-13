# [M] A heap use-after-free exists in wolfSSL's TLS 1.3 post-quantum cryptography (PQC) hybrid KeyShare...

## Summary
Severity: Medium
Advisory: JLSEC-2026-725
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-725
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
A heap use-after-free exists in wolfSSL's TLS 1.3 post-quantum cryptography (PQC) hybrid KeyShare processing. In the error handling path of `TLSX_KeyShare_ProcessPqcHybridClient()` in `src/tls.c`, the inner function `TLSX_KeyShare_ProcessPqcClient_ex()` frees a KyberKey object upon encountering an error. The caller then invokes `TLSX_KeyShare_FreeAll()`, which attempts to call ForceZero() on the already-freed KyberKey, resulting in writes of zero bytes over freed heap memory.

## References
- https://github.com/advisories/GHSA-w87p-fqgx-cqq8
- https://github.com/wolfssl/wolfssl/pull/10092
- https://nvd.nist.gov/vuln/detail/CVE-2026-5460
