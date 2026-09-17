# [H] `wolfSSL_X509_verify_cert` in the OpenSSL compatibility layer accepts a certificate chain in which...

## Summary
Severity: High
Advisory: JLSEC-2026-730
Ecosystem: Julia
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-730
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
`wolfSSL_X509_verify_cert` in the OpenSSL compatibility layer accepts a certificate chain in which the leaf's signature is not checked, if the attacker supplies an untrusted intermediate with Basic Constraints `CA:FALSE` that is legitimately signed by a trusted root. An attacker who obtains any leaf certificate from a trusted CA (e.g. a free DV cert from Let's Encrypt) can forge a certificate for any subject name with any public key and arbitrary signature bytes, and the function returns `WOLFSSL_SUCCESS` / `X509_V_OK`. The native wolfSSL TLS handshake path (`ProcessPeerCerts`) is not susceptible and the issue is limited to applications using the OpenSSL compatibility API directly, which would include integrations of wolfSSL into nginx and haproxy.

## References
- https://github.com/advisories/GHSA-hg75-4cmp-f367
- https://github.com/wolfSSL/wolfssl/pull/10102
- https://nvd.nist.gov/vuln/detail/CVE-2026-5501
