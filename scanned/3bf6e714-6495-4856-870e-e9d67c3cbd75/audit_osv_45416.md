# [M] Issue summary: An attacker-controlled CMP (Certificate Management Protocol) server could trigger...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1139
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1139
Type: osv

## Affected
- Julia: `AppBundler` — affected >=1.0.0 <1.0.1
- Julia: `OpenSSL_jll` — affected >=3.0.8+0 <3.5.7+0
- Julia: `Openresty_jll` — affected >=1.27.1+0

## Details
Issue summary: An attacker-controlled CMP (Certificate Management Protocol)
server could trigger a NULL pointer dereference in a CMP client application.

Impact summary: A NULL pointer dereference causes a crash of the
application and a Denial of Service.

An attacker controlling a CMP server (or acting as a man-in-the-middle) could
craft a CMP response containing a CRMF (Certificate Request Message Format)
CertRepMessage with an EncryptedValue structure where the symmAlg field
has an algorithm OID but no parameters field. When the OpenSSL CMP client
processes this response, the NULL dereference occurs, causing a crash of
the CMP client.

Applications that process untrusted CMP/CRMF messages may be affected.

The FIPS modules in 4.0, 3.6, 3.5, 3.4, and 3.0 are not affected by this
issue, as the affected code is outside the OpenSSL FIPS module boundary.

## References
- https://github.com/advisories/GHSA-gxhg-7jx8-m22j
- https://github.com/openssl/openssl/commit/61a86a8cd73546c9fea916f3d304c1293e05c046
- https://github.com/openssl/openssl/commit/665d5254083affde9982efca7c41dd01cacc8774
- https://github.com/openssl/openssl/commit/810b722f772652ad48042bcc7ab07e3414b11d0f
- https://github.com/openssl/openssl/commit/b90ff3b1bd33b1c18e6a09936d097c2eddef8873
- https://github.com/openssl/openssl/commit/e6f912907fc2ec82a0fd07aae55172c5e5e3d90d
- https://github.com/openssl/security/commit/61a86a8cd73546c9fea916f3d304c1293e05c046
- https://github.com/openssl/security/commit/665d5254083affde9982efca7c41dd01cacc8774
- https://github.com/openssl/security/commit/810b722f772652ad48042bcc7ab07e3414b11d0f
- https://github.com/openssl/security/commit/b90ff3b1bd33b1c18e6a09936d097c2eddef8873
- https://github.com/openssl/security/commit/e6f912907fc2ec82a0fd07aae55172c5e5e3d90d
- https://nvd.nist.gov/vuln/detail/CVE-2026-42767
- https://openssl-library.org/news/secadv/20260609.txt
