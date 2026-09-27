# [M] Envoy OAuth2 Filter: Padding Oracle via AES-256-CBC Cookie Decryption

## Summary
Severity: Medium
Advisory: BIT-envoy-2026-47775
Aliases: CVE-2026-47775, GHSA-396h-jpq4-vc7p
Ecosystem: Bitnami
Published: 2026-06-30
Source: https://osv.dev/vulnerability/BIT-envoy-2026-47775
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.38.0 <1.38.1

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. Prior to 1.35.11, 1.36.7, 1.37.3, and 1.38.1, the OAuth2 HTTP filter's encrypt()/decrypt() functions use AES-256-CBC without an authentication tag (no HMAC, no AEAD). The /callback endpoint returns HTTP 302 on successful decryption and HTTP 401 on padding failure, creating a padding oracle. An attacker who obtains the encrypted CodeVerifier cookie can recover the plaintext PKCE code_verifier in ~6,200 requests (~100 seconds), then exchange it with a stolen authorization code to obtain the victim's access token. This vulnerability is fixed in 1.35.11, 1.36.7, 1.37.3, and 1.38.1.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-396h-jpq4-vc7p
- https://nvd.nist.gov/vuln/detail/CVE-2026-47775
