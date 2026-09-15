# [H] wc_VerifyEccsiHash missing sanity check

## Summary
Severity: High
Advisory: CVE-2026-5466
CVSS: 7.5 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-5466
Type: osv

## Details
wolfSSL's ECCSI signature verifier `wc_VerifyEccsiHash` decodes the `r` and `s` scalars from the signature blob via `mp_read_unsigned_bin` with no check that they lie in `[1, q-1]`. A crafted forged signature could verify against any message for any identity, using only publicly-known constants.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5466.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5466
- https://github.com/wolfssl/wolfssl/pull/10102
