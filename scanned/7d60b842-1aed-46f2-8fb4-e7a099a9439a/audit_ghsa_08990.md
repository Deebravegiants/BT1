# [M] Symfony has an Argument Injection in SendmailTransport via Dash-Prefixed Recipient Address

## Summary
Severity: Medium
Advisory: GHSA-xx3c-qf5g-hc39
CVE: CVE-2026-45068
CWE: CWE-88
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-xx3c-qf5g-hc39
Type: github-advisory

## Affected
- Packagist: `symfony/mailer` — affected >=0 <5.4.52
- Packagist: `symfony/symfony` — affected >=0 <5.4.52
- Packagist: `symfony/mailer` — affected >=6.0.0 <6.4.40
- Packagist: `symfony/mailer` — affected >=7.0.0 <7.4.12
- Packagist: `symfony/mailer` — affected >=8.0.0 <8.0.12
- Packagist: `symfony/symfony` — affected >=6.0.0 <6.4.40
- Packagist: `symfony/symfony` — affected >=7.0.0 <7.4.12
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.12

## Details
### Description

Symfony Mailer selects a transport via the `MAILER_DSN` environment variable / configuration (e.g. `smtp://...`, `sendmail://...`, `native://default`). `SendmailTransport` invokes the local `sendmail` binary and supports two modes: `-bs` (speak SMTP over stdin: the default) and `-t` (read the message on stdin, pass recipients as command-line arguments).

In `-t` mode, recipient addresses are appended to the sendmail command line **without a `--` end-of-options separator**. A recipient address beginning with `-` (which `Symfony\Component\Mime\Address` accepts as valid) is therefore interpreted by sendmail as a command-line option rather than an address.

### Resolution

The `SendmailTransport` transport now ensure `--` is set before the list of recipients.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/c45144862dc289d03952f41f6078174089a3afc6) for branch 5.4.

### Credits

Symfony would like to thank Claude Mythos Preview (via Project Glasswing) for reporting the issue and providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-xx3c-qf5g-hc39
- https://github.com/symfony/symfony/commit/c45144862dc289d03952f41f6078174089a3afc6
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/mailer/CVE-2026-45068.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-45068.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-45068
