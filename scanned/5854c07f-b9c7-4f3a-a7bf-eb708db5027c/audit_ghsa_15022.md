# [H] typo3 Security fix for Flow Swift Mailer package

## Summary
Severity: High
Advisory: GHSA-xjw3-5r5c-m5ph
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-xjw3-5r5c-m5ph
Type: github-advisory

## Affected
- Packagist: `typo3/swiftmailer` — affected >=4.1.0 <4.1.99
- Packagist: `typo3/swiftmailer` — affected >=5.4.0 <5.4.5

## Details
A remote code execution vulnerability has been found in the Swift Mailer library (swiftmailer/swiftmailer) recently. See this advisory for details. If you are not using the default mail() transport, this particular problem  does not affect you. Upgrading is of course still recommended!

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/swiftmailer/2017-01-06.yaml
- https://github.com/neos/swiftmailer
- https://www.neos.io/blog/flow-sa-2017-01.html
