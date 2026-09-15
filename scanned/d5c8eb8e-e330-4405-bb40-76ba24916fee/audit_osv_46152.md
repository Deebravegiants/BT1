# [M] `wolfSSL_PKCS7_verify()` returning success for a degenerate (certs-only) PKCS#7 object that contains...

## Summary
Severity: Medium
Advisory: JLSEC-2026-736
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-736
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
`wolfSSL_PKCS7_verify()` returning success for a degenerate (certs-only) PKCS#7 object that contains no signer. Such an object has empty signerInfos, so the underlying signed-data verification succeeds without authenticating any content. The compatibility-layer verify path now rejects the object when no signer signature has actually been verified, so a PKCS#7 carrying no valid signature is no longer reported as verified. This is enforced regardless of the `PKCS7_NOVERIFY` flag, which only suppresses signer certificate chain validation and was never intended to waive the requirement that a signature exist. Only affects OpenSSL compatibility builds that call the `PKCS7_verify()` compatibility API on potentially degenerate PKCS#7 bundles.

## References
- https://github.com/advisories/GHSA-cj56-5c53-9qjf
- https://github.com/wolfSSL/wolfssl/pull/10702
- https://nvd.nist.gov/vuln/detail/CVE-2026-55961
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
