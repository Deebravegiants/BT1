# [C] In `TLSX_EchChangeSNI`, the ctx->extensions branch set extensions unconditionally even when...

## Summary
Severity: Critical
Advisory: JLSEC-2026-731
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-731
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
In `TLSX_EchChangeSNI`, the ctx->extensions branch set extensions unconditionally even when `TLSX_Find` returned NULL. This caused `TLSX_UseSNI` to attach the attacker-controlled publicName to the shared `WOLFSSL_CTX` when no inner SNI was configured. `TLSX_EchRestoreSNI` then failed to clean it up because its removal was gated on serverNameX != NULL. The inner ClientHello was sized before the pollution but written after it, causing `TLSX_SNI_Write` to memcpy 255 bytes past the allocation boundary.

## References
- https://github.com/advisories/GHSA-65xm-pfx9-g5p3
- https://github.com/wolfSSL/wolfssl/pull/10102
- https://nvd.nist.gov/vuln/detail/CVE-2026-5503
