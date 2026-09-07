# [H] DDOS attack on graphql endpoints

## Summary
Severity: High
Advisory: GHSA-67g8-c724-8mp3
CVE: CVE-2023-28104
CWE: CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-16
Source: https://github.com/advisories/GHSA-67g8-c724-8mp3
Type: github-advisory

## Affected
- Packagist: `silverstripe/graphql` — affected >=4.1.1 <4.1.2
- Packagist: `silverstripe/graphql` — affected >=4.2.2 <4.2.3

## Details
An attacker could use a specially crafted graphql query to execute a Distributed Denial of Service attack (DDOS attack) against a website. This mostly affects websites with publicly exposed and particularly large/complex graphql schemas.

If your Silverstripe CMS project does not expose a public facing graphql schema, a user account is required to trigger the DDOS attack. If your site is hosted behind a content delivery network (CDN), such as Imperva or CloudFlare, this will likely further mitigate the risk.

Upgrade to `silverstripe/graphql` 4.2.3 or 4.1.2 or above to remedy the vulnerability.

## References
- https://github.com/silverstripe/silverstripe-graphql/security/advisories/GHSA-67g8-c724-8mp3
- https://nvd.nist.gov/vuln/detail/CVE-2023-28104
- https://github.com/silverstripe/silverstripe-graphql/pull/526
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/graphql/CVE-2023-28104.yaml
- https://github.com/silverstripe/silverstripe-graphql
- https://github.com/silverstripe/silverstripe-graphql/releases/tag/4.1.2
- https://github.com/silverstripe/silverstripe-graphql/releases/tag/4.2.3
- https://www.silverstripe.org/download/security-releases/CVE-2023-28104
