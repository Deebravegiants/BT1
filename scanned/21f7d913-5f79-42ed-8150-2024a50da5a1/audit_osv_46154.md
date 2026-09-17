# [M] Chain intermediate CA:TRUE without keyCertSign accepted as a signing CA

## Summary
Severity: Medium
Advisory: JLSEC-2026-738
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-738
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.8.4+0 <5.9.2+0

## Details
Chain intermediate CA:TRUE without keyCertSign accepted as a signing CA. Intermediate CA certificates are required to have the keyCertSign key usage when a Key Usage extension is present, but chain-supplied temporary CAs (`WOLFSSL_TEMP_CA`) added while building a certificate path were previously exempted from this check, so an intermediate asserting CA:TRUE but lacking keyCertSign was accepted as a signing CA. The check now applies to chain-supplied temporary CAs as well; only operator-loaded root certificates (`WOLFSSL_USER_CA`) and self-signed roots remain exempt. Per RFC 5280 an absent Key Usage extension implies all usages, so the requirement is enforced only when the extension is actually present (extKeyUsageSet). Affects the OpenSSL-compatibility certificate-path-building path (`X509_verify_cert` / `X509_STORE`, `OPENSSL_EXTRA/OPENSSL_ALL`), where untrusted chain intermediates are added as temporary CAs; native (non-OpenSSL-compat) certificate verification does not create temporary CAs and is unaffected. Within those builds, the check applies unless `ALLOW_INVALID_CERTSIGN` is defined.

## References
- https://github.com/advisories/GHSA-68g3-7fhp-7rg3
- https://github.com/wolfSSL/wolfssl/pull/10702
- https://nvd.nist.gov/vuln/detail/CVE-2026-55964
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
