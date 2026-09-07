# [H] Symfony has Email Header / SMTP Command Injection via CRLF in Symfony\Component\Mime\Address

## Summary
Severity: High
Advisory: GHSA-qpmx-3rfj-7rhv
CVE: CVE-2026-45067
CWE: CWE-93
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-qpmx-3rfj-7rhv
Type: github-advisory

## Affected
- Packagist: `symfony/mime` — affected >=0 <5.4.52
- Packagist: `symfony/symfony` — affected >=0 <5.4.52
- Packagist: `symfony/mime` — affected >=6.0.0 <6.4.40
- Packagist: `symfony/mime` — affected >=7.0.0 <7.4.12
- Packagist: `symfony/mime` — affected >=8.0.0 <8.0.12
- Packagist: `symfony/symfony` — affected >=6.0.0 <6.4.40
- Packagist: `symfony/symfony` — affected >=7.0.0 <7.4.12
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.12

## Details
### Description

`Symfony\Component\Mime\Address` is the value-object every Symfony Mailer address (to/cc/bcc/from/reply-to) flows through; its constructor is documented as validating the address and throwing on invalid input, so developers treat it as a security boundary.

The constructor accepts email addresses whose local-part (the part before `@`) is an RFC-5322 *quoted string* containing raw `\r\n` bytes, e.g. `"x\r\nBcc: attacker@evil"@example.com`. The stored address is later emitted verbatim into (1) the rendered message headers and (2) `SmtpTransport`'s `MAIL FROM:<...>` / `RCPT TO:<...>` protocol lines, turning the embedded CRLF into a new mail header and/or a new SMTP command.

### Resolution

The `Address` constructor now rejects addresses containing line breaks.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/dc2dbd29211eb4ddc451373fa1374fb926e94604) for branch 5.4.

### Credits

We would like to thank Claude Mythos Preview (via Project Glasswing) for reporting the issue and providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-qpmx-3rfj-7rhv
- https://github.com/symfony/symfony/commit/dc2dbd29211eb4ddc451373fa1374fb926e94604
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/mime/CVE-2026-45067.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-45067.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-45067
