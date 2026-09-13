# [M] wolfSSL_PKCS7_verify() reports success for degenerate (certs-only) PKCS#7 with no signer

## Summary
Severity: Medium
Advisory: CVE-2026-55961
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-55961
Type: osv

## Details
wolfSSL_PKCS7_verify() returning success for a degenerate (certs-only) PKCS#7 object that contains no signer. Such an object has empty signerInfos, so the underlying signed-data verification succeeds without authenticating any content. The compatibility-layer verify path now rejects the object when no signer signature has actually been verified, so a PKCS#7 carrying no valid signature is no longer reported as verified. This is enforced regardless of the PKCS7_NOVERIFY flag, which only suppresses signer certificate chain validation and was never intended to waive the requirement that a signature exist. Only affects OpenSSL compatibility builds that call the PKCS7_verify() compatibility API on potentially degenerate PKCS#7 bundles.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55961.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55961
- https://github.com/wolfSSL/wolfssl/pull/10702
- https://github.com/wolfSSL/wolfssl
