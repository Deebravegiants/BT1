# [H] Improper Certificate Signature Verification in X.509 Chain Validation Allows Forged Leaf Certificates

## Summary
Severity: High
Advisory: CVE-2026-5501
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-5501
Type: osv

## Details
wolfSSL_X509_verify_cert in the OpenSSL compatibility layer accepts a certificate chain in which the leaf's signature is not checked, if the attacker supplies an untrusted intermediate with Basic Constraints `CA:FALSE` that is legitimately signed by a trusted root. An attacker who obtains any leaf certificate from a trusted CA (e.g. a free DV cert from Let's Encrypt) can forge a certificate for any subject name with any public key and arbitrary signature bytes, and the function returns `WOLFSSL_SUCCESS` / `X509_V_OK`. The native wolfSSL TLS handshake path (`ProcessPeerCerts`) is not susceptible and the issue is limited to applications using the OpenSSL compatibility API directly, which would include integrations of wolfSSL into nginx and haproxy.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5501.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5501
- https://github.com/wolfSSL/wolfssl/pull/10102
