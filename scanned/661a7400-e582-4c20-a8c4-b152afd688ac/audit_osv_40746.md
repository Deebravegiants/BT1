# [H] Client-Side Memory Leak in OCSP Response Checking

## Summary
Severity: High
Advisory: CVE-2026-54876
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-54876
Type: osv

## Details
Issue summary: A malicious TLS server can cause a memory leak in a TLS
client that has enabled OCSP response checking by sending an OCSP
response that contains no single response entries.

Impact summary: An attacker can leak an attacker-tunable amount of memory
per TLS handshake in a victim client application. A long-running client
that repeatedly connects to a malicious server can have its memory
exhausted, resulting in a Denial of Service.

CWE: CWE-401: Missing Release of Memory after Effective Lifetime

Description: The affected function is called during X.509 certificate
chain verification when OCSP response checking is enabled
with the X509_V_FLAG_OCSP_RESP_CHECK or X509_V_FLAG_OCSP_RESP_CHECK_ALL
verification flags, for example when a TLS client verifies an OCSP
response stapled into the TLS handshake by the server.

When the received BasicOCSPResponse contains an empty SEQUENCE OF
SingleResponse, which is permitted on the wire and accepted by the
OpenSSL decoder, the OCSP_BASICRESP structure allocated by
OCSP_response_get1_basic() was not freed because an early return
bypassed the cleanup code at the end of the function.

The amount of memory leaked per handshake can be amplified by the
attacker by padding the certs field of the BasicOCSPResponse with
bogus certificates, which are parsed and stored in the leaked
structure before the empty response check triggers the early return.
A long-running TLS client that repeatedly connects to a malicious
server can have its memory exhausted over time.

OCSP response checking is not enabled by default. Only client
applications that explicitly enable the OCSP response check
verification flags are affected.

FIPS impact: no

The FIPS modules in 4.0 and 3.6 are not affected by this issue as the
affected code is outside the OpenSSL FIPS module boundary.

## References
- http://www.openwall.com/lists/oss-security/2026/08/05/8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54876.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-54876
- https://openssl-library.org/news/secadv/20260805.txt
- https://github.com/openssl/openssl/commit/155b5fe0f93365e6df1c56ee3606b121080c6c12
- https://github.com/openssl/openssl/commit/d8c51048ac037a21bae0f41cad7a3920dc7f3638
