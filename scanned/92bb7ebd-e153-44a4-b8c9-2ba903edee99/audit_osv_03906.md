# [C] ALPINE-CVE-2026-63073

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-63073
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-63073
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=0 <3.5.8-r0
- Alpine:v3.23: `openssl` — affected >=0 <3.5.8-r0
- Alpine:v3.24: `openssl` — affected >=0 <3.5.8-r0

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
- https://security.alpinelinux.org/vuln/CVE-2026-63073
