# [H] http4k: `HmacSha256.hash` (despite the `Hmac` naming) computed a plain unkeyed digest; clarified by deprecation in favour of `Sha256.hash` / `Sha256.hmac`

## Summary
Severity: High
Advisory: GHSA-m4w9-hjfw-vwj4
CWE: CWE-345
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-m4w9-hjfw-vwj4
Type: github-advisory

## Affected
- Maven: `org.http4k:http4k-core` — affected >=0 <6.49.0.0

## Details
### Impact

The `HmacSha256` class contained two functions:
- `hash(payload)` — a plain unkeyed SHA-256 digest. The `Hmac` prefix in the class name was misleading; this function has no key parameter, so it could never have been an HMAC.
- `hmacSHA256(key, data)` — a properly keyed HMAC-SHA256.

A reader who didn't engage with the function signature could in principle have assumed `HmacSha256.hash(payload)` was somehow keyed, but the absence of any key parameter made that misuse unlikely in practice.

**Who is affected:** any downstream caller who read the class name and used `HmacSha256.hash` as a message authentication code without noticing it takes no key. **Verified at v6.47.2.0: zero internal misuse in http4k itself.** Both production usages of `HmacSha256.hash` (AWS SigV4 canonical-request hashing in `AwsSignatureV4Signer.kt` and `x-amz-content-sha256` in `awsExtensions.kt`) are AWS-spec-correct uses of plain SHA-256; every keyed `hmacSHA256(key, data)` call passes a real key. The advisory exists so any downstream caller relying on the misleadingly-named API knows to migrate.

### Patches

Upgrade to **6.49.0.0** or later. The fix introduces:
- `Sha256.hash(input)` — unkeyed digest (the actual behaviour `HmacSha256.hash` provided).
- `Sha256.hmac(key, input)` — keyed HMAC-SHA256 (the behaviour the name implied).

`HmacSha256` is deprecated. Existing callers continue to work via deprecation shims; migrate to `Sha256.hash` or `Sha256.hmac` per intent.

### Workarounds

If you cannot upgrade and you need a real HMAC-SHA256, use `javax.crypto.Mac.getInstance("HmacSHA256")` with a `SecretKeySpec`. For an unkeyed SHA-256 digest, use `java.security.MessageDigest.getInstance("SHA-256")`. The keyed `hmacSHA256(key, data)` was always correctly implemented and is safe to use as-is.

### References

- Fix release: [v6.49.0.0](https://github.com/http4k/http4k/releases/tag/6.49.0.0)
- Background: [RFC 2104 — HMAC: Keyed-Hashing for Message Authentication](https://datatracker.ietf.org/doc/html/rfc2104)

## References
- https://github.com/http4k/http4k/security/advisories/GHSA-m4w9-hjfw-vwj4
- https://datatracker.ietf.org/doc/html/rfc2104
- https://github.com/http4k/http4k
- https://github.com/http4k/http4k/releases/tag/6.49.0.0
