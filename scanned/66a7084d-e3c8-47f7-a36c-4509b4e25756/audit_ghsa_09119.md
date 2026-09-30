# [H] Symfony Vulnerable to Identity Spoofing via Unanchored DN Regex in X509Authenticator

## Summary
Severity: High
Advisory: GHSA-ph86-p8f6-f9r2
CVE: CVE-2026-45063
CWE: CWE-290
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-ph86-p8f6-f9r2
Type: github-advisory

## Affected
- Packagist: `symfony/security-http` — affected >=0 <5.4.52
- Packagist: `symfony/security-http` — affected >=6.0.0-BETA1 <6.4.40
- Packagist: `symfony/security-http` — affected >=7.0.0-BETA1 <7.4.12
- Packagist: `symfony/security-http` — affected >=8.0.0-BETA1 <8.0.12
- Packagist: `symfony/symfony` — affected >=0 <5.4.52
- Packagist: `symfony/symfony` — affected >=6.0.0-BETA1 <6.4.40
- Packagist: `symfony/symfony` — affected >=7.0.0-BETA1 <7.4.12
- Packagist: `symfony/symfony` — affected >=8.0.0-BETA1 <8.0.12

## Details
### Description

`X509Authenticator` implements client-certificate (mTLS) authentication: the web server validates the client's certificate against a trusted CA, then passes the certificate's Subject DN (Distinguished Name: a string like `CN=Alice,O=Example,emailAddress=alice@example.com`) to Symfony via `$_SERVER['SSL_CLIENT_S_DN']`. Symfony extracts the user identifier from that string.

The extraction uses an **unanchored** regex that matches `emailAddress=` anywhere in the DN string: including inside the *value* of a different RDN (Relative Distinguished Name: one `key=value` component of the DN), such as `CN`. An attacker who can obtain a certificate from a trusted CA with a free-text `CN` can smuggle `emailAddress=victim@target` inside the CN value and be authenticated as the victim.

### Resolution

The `X509Authenticator` now uses a regex that anchors the match to an RDN boundary (start of string, or following a `,` / `/` separator).

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/ccb3f724c7ff55670a6fe3521c7bf1514cceb478) for branch 5.4.

### Credits

Symfony would like to thank Claude Mythos Preview (via Project Glasswing) for reporting the issue and providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-ph86-p8f6-f9r2
- https://github.com/symfony/symfony/commit/ccb3f724c7ff55670a6fe3521c7bf1514cceb478
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2026-45063.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-45063.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-45063
