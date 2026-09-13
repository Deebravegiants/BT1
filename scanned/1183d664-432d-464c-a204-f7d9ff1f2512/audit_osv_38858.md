# [H] NULL Dereference in Certificate Verification with OCSP Checking

## Summary
Severity: High
Advisory: CVE-2026-42765
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-42765
Type: osv

## Details
Issue summary: When a partial-chain certificate verification is enabled
together with OCSP response checking for the whole chain, a NULL dereference
will happen if the verified chain does not have a self-signed trusted anchor,
crashing the process.

Impact summary: A NULL pointer dereference can trigger a crash which leads to a
Denial of Service for an application.

When performing OCSP response checking for certificates in the verification
chain, the code always tries to access the next certificate as the issuer.
There is a check for a self-signed certificate. However with the partial
chain verification enabled when the chain does not have a self-signed trusted
anchor, the issuer will be NULL for the last certificate in the chain. A NULL
pointer dereference then happens.

This issue affects only applications which enable both OCSP verification
of the certificate chain (X509_V_FLAG_OCSP_RESP_CHECK_ALL) and partial
chain verification (X509_V_FLAG_PARTIAL_CHAIN) in the certificate
verification. Both flags are disabled by default. For that reason, we have
assigned Low severity to the issue.

No FIPS modules are affected by this issue as the affected code is outside
the OpenSSL FIPS module boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42765.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42765
- https://openssl-library.org/news/secadv/20260609.txt
- https://github.com/openssl/openssl/commit/14340b7fa1d444615486bc137014b064e64ec334
- https://github.com/openssl/openssl/commit/eb345da18ce2216b2f3ade9c2bc23e068487fa97
