# [C] Swiftmailer Sendmail transport arbitrary shell execution

## Summary
Severity: Critical
Advisory: GHSA-4qpj-gxxg-jqg4
Ecosystem: Packagist
Published: 2024-05-29
Source: https://github.com/advisories/GHSA-4qpj-gxxg-jqg4
Type: github-advisory

## Affected
- Packagist: `swiftmailer/swiftmailer` — affected >=4.0.0 <5.2.1

## Details
Prior to 5.2.1, the sendmail transport (`Swift_Transport_SendmailTransport`) was vulnerable to an arbitrary shell execution if the "From" header came from a non-trusted source and no "Return-Path" is configured. This has been fixed in 5.2.1. If you are using sendmail as a transport, you are encouraged to upgrade as soon as possible.

## References
- https://github.com/swiftmailer/swiftmailer/commit/b4b78af55e5e87f5ff07c06c6be7963c44562f80
- https://github.com/swiftmailer/swiftmailer/commit/efc430606a5faed864b969adfbdc5363ce2115a2
- https://github.com/FriendsOfPHP/security-advisories/blob/master/swiftmailer/swiftmailer/2014-06-13.yaml
- https://github.com/swiftmailer/swiftmailer
- https://web.archive.org/web/20150219063146/http://blog.swiftmailer.org/post/88660759928/security-fix-swiftmailer-5-2-1-released
- http://blog.swiftmailer.org/post/88660759928/security-fix-swiftmailer-5-2-1-released
