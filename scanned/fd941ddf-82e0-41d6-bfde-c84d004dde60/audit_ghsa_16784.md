# [C] Flow Swift Mailer package Remote code execution

## Summary
Severity: Critical
Advisory: GHSA-rq6q-hjvh-5mwh
Ecosystem: Packagist
Published: 2024-05-17
Source: https://github.com/advisories/GHSA-rq6q-hjvh-5mwh
Type: github-advisory

## Affected
- Packagist: `neos/swiftmailer` — affected >=0 <5.4.5

## Details
A remote code execution vulnerability has been found in the Swift Mailer library (swiftmailer/swiftmailer) recently. [See this advisory for details](http://legalhackers.com/advisories/SwiftMailer-Exploit-Remote-Code-Exec-CVE-2016-10074-Vuln.html). If you are not using the default mail() transport, this particular problem  does not affect you. Upgrading is of course still recommended!

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/neos/swiftmailer/2017-01-06.yaml
- https://github.com/neos/swiftmailer
- https://www.neos.io/blog/flow-sa-2017-01.html
