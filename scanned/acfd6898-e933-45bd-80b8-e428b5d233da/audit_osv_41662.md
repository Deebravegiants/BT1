# [C] Untrusted Sender DN Used as Format String in CMP Response Validation

## Summary
Severity: Critical
Advisory: CVE-2026-63073
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-63073
Type: osv

## Details
Issue summary: OpenSSL CMP response validation passed an unexpected response
sender distinguished name directly as the format string to `ERR_raise_data()`.

Impact summary: A malicious or intercepted CMP endpoint can crash a CMP client
that enforces an expected sender or uses a pinned server certificate whose
subject becomes the default expected sender.

CWE: CWE-134 (Use of Externally-Controlled Format String)

Description: When validating a received CMP message, ossl_cmp_msg_check_update()
converts the peer-supplied sender distinguished name with X509_NAME_oneline()
and passes it directly as the format argument to ERR_raise_data(). Percent
characters survive the conversion, so a sender DN such as "CN=%s%n" reaches
BIO_vsnprintf() as an attacker-controlled format string with no matching variadic
arguments. This path is only reached when the caller configures an expected
sender or pins a server certificate, which is the normal configuration for a
CMP client validating server responses.

Since the attacker controls the format string but none of the variadic
arguments, such specifiers as %s and %n dereference or write through unrelated
stack contents and crash the client. The reliable consequence is a denial of
service, when the response comes from a malicious or intercepted CMP endpoint.
There is no controlled memory write, arbitrary-address read, or reliable path
to remote code execution.

FIPS impact: no

No FIPS modules are affected by this issue, as the CMP protocol
implementation is outside the OpenSSL FIPS module boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63073.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63073
- https://openssl-library.org/news/secadv/20260825.txt
- https://github.com/openssl/openssl/commit/0cc20b322639919aa423e90799d9a57c3b4b76ca
- https://github.com/openssl/openssl/commit/6a0acc072b4d37a7cac1252a29c1ce1f00c5ec29
- https://github.com/openssl/openssl/commit/7eb2e3ec9d1d4f35c8022fccd4b03398b3f33e21
- https://github.com/openssl/openssl/commit/a7e5a6eea8fd3ccca6b6fbba031a5fbf8a3d93b4
