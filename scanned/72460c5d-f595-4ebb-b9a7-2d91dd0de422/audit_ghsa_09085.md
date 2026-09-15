# [M] Symfony: Twilio SMS Notifier allows unauthenticated webhook injection due to missing X-Twilio-Signature verification

## Summary
Severity: Medium
Advisory: GHSA-55rj-x2vc-4whq
CVE: CVE-2026-47212
CWE: CWE-306, CWE-347
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-55rj-x2vc-4whq
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=6.4.0 <6.4.40
- Packagist: `symfony/symfony` — affected >=7.0.0 <7.4.12
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.12
- Packagist: `symfony/twilio-notifier` — affected >=6.4.0 <6.4.40
- Packagist: `symfony/twilio-notifier` — affected >=7.0.0 <7.4.12
- Packagist: `symfony/twilio-notifier` — affected >=8.0.0 <8.0.12

## Details
### Description

The Twilio SMS notifier bridge ships a webhook request parser used to authenticate and decode the status callbacks Twilio POSTs to an application's webhook endpoint. Its `doParse(Request $request, #[\SensitiveParameter] string $secret)` method receives the configured webhook secret but never reads it; it decodes and returns the payload unconditionally, ignoring the `X-Twilio-Signature` HMAC header Twilio sends with each request.

As a result, an application that wires up the Twilio webhook endpoint accepts **any** POST to that URL, even when a signing secret is configured (the recommended setup). An attacker who knows the endpoint exists can submit forged status payloads, fake delivered / failed / undelivered events, leading to delivery-metrics fraud, downstream automation triggers, etc.

### Resolution

`TwilioRequestParser::doParse()` now requires and verifies the `X-Twilio-Signature` header (HMAC-SHA1 over the full request URL concatenated with the alphabetically-sorted POST parameters, base64-encoded, keyed with the Twilio account auth token) before further processing, using a constant-time comparison.

When no secret is configured the behaviour is unchanged: signature verification remains opt-in, but it is now actually enforced once opted in.

Applications behind a TLS-terminating reverse proxy must configure `framework.trusted_proxies` and `framework.trusted_headers` so that `Request::getUri()` returns the public URL Twilio signed.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/8545fb2af6c07dfb5ef0fc8d9bccf86db2c94356) for branch 6.4.

### Credits

Symfony would like to thank Himanshu Anand for reporting the issue and Nicolas Grekas for providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-55rj-x2vc-4whq
- https://github.com/symfony/symfony/commit/8545fb2af6c07dfb5ef0fc8d9bccf86db2c94356
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-47212.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/twilio-notifier/CVE-2026-47212.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-47212
