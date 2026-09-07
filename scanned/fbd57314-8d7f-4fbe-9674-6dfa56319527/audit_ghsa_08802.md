# [M] Symfony's Mailtrap Mailer Webhook Parser Never Verifies the X-Mt-Signature HMAC — Unauthenticated Webhook Event Injection

## Summary
Severity: Medium
Advisory: GHSA-59f3-vp2f-mp9w
CVE: CVE-2026-45755
CWE: CWE-306, CWE-347
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-59f3-vp2f-mp9w
Type: github-advisory

## Affected
- Packagist: `symfony/mailtrap-mailer` — affected >=7.2.0 <7.4.12
- Packagist: `symfony/mailtrap-mailer` — affected >=8.0.0 <8.0.12
- Packagist: `symfony/symfony` — affected >=7.2.0 <7.4.12
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.12

## Details
### Description

The Mailtrap mailer bridge ships a webhook request parser used to authenticate and decode the event callbacks Mailtrap POSTs to an application's webhook endpoint. Its `doParse(Request $request, #[\SensitiveParameter] string $secret)` method receives the configured webhook secret but never reads it; it decodes and returns the payload unconditionally, ignoring the `X-Mt-Signature` HMAC header Mailtrap sends with each request.

As a result, an application that wires up the Mailtrap webhook endpoint accepts **any** POST to that URL, even when a signing secret is configured (the recommended setup). An attacker who knows the endpoint exists can submit forged event payloads, fake delivery / bounce / open / click / spam events, leading to suppression-list corruption, delivery-metrics fraud, etc.

### Resolution

`MailtrapRequestParser::doParse()` now requires and verifies the `X-Mt-Signature` header, an HMAC-SHA256 of the raw request body keyed with the configured secret, before decoding the payload, using a constant-time comparison.

When no secret is configured the behaviour is unchanged: signature verification remains opt-in, but it is now actually enforced once opted in.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/4e0467e4e182cf2e704a3d9e1bc1a6be65d52ab8) for branch 7.4.

### Credits

Symfony would like to thank Himanshu Anand for reporting the issue and Alexandre Daubois providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-59f3-vp2f-mp9w
- https://github.com/symfony/symfony/commit/4e0467e4e182cf2e704a3d9e1bc1a6be65d52ab8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/mailtrap-mailer/CVE-2026-45755.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-45755.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-45755
