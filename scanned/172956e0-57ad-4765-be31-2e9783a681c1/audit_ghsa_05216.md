# [M] Symfony: Mailomat Mailer Webhook Parser Reads the HMAC Algorithm from the Request: Signature Algorithm Downgrade

## Summary
Severity: Medium
Advisory: GHSA-rrj9-5q2j-4gvr
CVE: CVE-2026-48747
CWE: CWE-347, CWE-757
Ecosystem: Packagist
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-rrj9-5q2j-4gvr
Type: github-advisory

## Affected
- Packagist: `symfony/mailomat-mailer` — affected >=7.2.0 <7.4.13
- Packagist: `symfony/mailomat-mailer` — affected >=8.0.0 <8.0.13
- Packagist: `symfony/symfony` — affected >=7.2.0 <7.4.13
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.13

## Details
### Description

`Symfony\Component\Mailer\Bridge\Mailomat\Webhook\MailomatRequestParser::validateSignature()` parses the `X-MOM-Webhook-Signature` request header as `algo=signature` and passes the wire-supplied `$algo` directly to `hash_hmac()` when verifying the request against the configured webhook secret. The request therefore selects the HMAC primitive used to authenticate it.

PHP's `hash_hmac()` enforces only that the chosen algorithm is HMAC-compatible. That set still includes primitives with known cryptanalysis (`md4`, `md5`, `ripemd128`, `tiger128,3`, … — e.g. existential forgery of HMAC-MD4, Contini & Yin, ASIACRYPT 2006). This is the canonical algorithm-confusion shape, analogous to JWT `alg=none` / `alg=HS256` downgrades: any future cryptographic weakness in any HMAC primitive PHP exposes becomes immediately exploitable against a Mailomat webhook receiver, the moment an attacker is in a position to compute a signature for that primitive, without a code change on the Symfony side.

Mailomat's [documented webhook security](https://api.mailomat.swiss/docs/#tag/webhook-security) pins SHA-256; the parser did not.

### Resolution

`MailomatRequestParser::validateSignature()` now requires the signature header to be of the form `sha256=<hex>` and verifies the signature with HMAC-SHA256 keyed by the configured secret using a constant-time comparison. Any other algorithm declared on the wire (including the HMAC primitives PHP would otherwise accept) is rejected.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/bdfe9fe0d94d33dfaca0bc2fe0b00b54767b0c88) for branch 7.4 (and forward-ported to 8.0 and 8.1).

### Credits

Symfony would like to thank Omar Alshammari, Essam Alanazi and Alwaleed Alshammari for reporting the issue and Nicolas Grekas for providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-rrj9-5q2j-4gvr
- https://github.com/symfony/symfony/commit/bdfe9fe0d94d33dfaca0bc2fe0b00b54767b0c88
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/mailomat-mailer/CVE-2026-48747.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-48747.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-48747
