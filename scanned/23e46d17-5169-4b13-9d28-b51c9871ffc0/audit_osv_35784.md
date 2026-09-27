# [H] RPK Server Signature Algorithm Selection Can Dereference a Missing Certificate

## Summary
Severity: High
Advisory: CVE-2026-14457
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-14457
Type: osv

## Details
Issue summary: In a server or client configuration with RFC7250 Raw Public Keys (RPKs)
enabled, and only the private key (with no associated certificate) configured locally,
a NULL pointer dereference may occur when the remote peer solicits raw public keys and
also sends the typically omitted "signature_algorithms_cert" TLS extension.

Impact summary: The impact is limited to a possible Denial of Service as a result of
an application abort, no data disclosure or remote command execution are possible.

CWE: CWE-476: NULL Pointer Dereference

Description: While a passing comment in sample code in the documentation suggests
that key-only RPK configurations are supported, the best-practice RPK configuration
is to always configure a corresponding certificate (possibly self-signed or
signed by any convenient CA).

When the private key is configured along with a matching certificate, the
"signature_algorithms_cert" extension is handled reliably even without the
fix, and peer clients or servers that don't support raw public keys may be
able to complete a TLS connection by pinning or verifying the corresponding
certificate or its public key.

Deployments that prefer to configure just a private key with no certificate
need to upgrade to an updated release as noted below.

FIPS impact: no

No FIPS modules are affected by this issue, as the SSL protocol implementation
is outside the OpenSSL FIPS module boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14457.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14457
- https://openssl-library.org/news/secadv/20260825.txt
- https://github.com/openssl/openssl/commit/1e8c398db67404babd3e5af999bb6bd86f720c76
- https://github.com/openssl/openssl/commit/581aaa0f0a35d214740f0fe1f5283ec41f1212e1
- https://github.com/openssl/openssl/commit/d0af20478688a6aa2f59d61caa3f82136b181d7f
- https://github.com/openssl/openssl/commit/dad836b071da6579510c968615848ba03cac593b
