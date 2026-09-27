# [H] wolfSSL's ECCSI signature verifier `wc_VerifyEccsiHash` decodes the `r` and `s` scalars from the...

## Summary
Severity: High
Advisory: JLSEC-2026-726
Ecosystem: Julia
CVSS: 7.5 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-726
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
wolfSSL's ECCSI signature verifier `wc_VerifyEccsiHash` decodes the `r` and `s` scalars from the signature blob via `mp_read_unsigned_bin` with no check that they lie in `[1, q-1]`. A crafted forged signature could verify against any message for any identity, using only publicly-known constants.

## References
- https://github.com/advisories/GHSA-47qf-hp3h-rwmm
- https://github.com/wolfssl/wolfssl/pull/10102
- https://nvd.nist.gov/vuln/detail/CVE-2026-5466
