# [M] SimpleSAMLphp Link Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-v858-922f-fj9v
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-v858-922f-fj9v
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp` — affected >=0 <1.14.4

## Details
### Background
Several scripts part of SimpleSAMLphp display a web page with links obtained from the request parameters. This allows us to enhance usability, as the users are presented with links they can follow after completing a certain action, like logging out.

### Description
The following scripts were not checking the URLs obtained via the HTTP request before displaying them as the target of links that the user may click on:

- www/logout.php
- modules/core/www/no_cookie.php
The issue allowed attackers to display links targeting a malicious website inside a trusted site running SimpleSAMLphp, due to the lack of security checks involving the link_href and retryURL HTTP parameters, respectively. The issue was resolved by including a verification of the URLs received in the request against a white list of websites specified in the trusted.url.domains configuration option.

### Affected versions
All SimpleSAMLphp versions prior to 1.14.4.

### Impact
A remote attacker could craft a link pointing to a trusted website running SimpleSAMLphp, including a parameter pointing to a malicious website, and try to fool the victim into visiting that website by clicking on a link in the page presented by SimpleSAMLphp.

## References
- https://github.com/simplesamlphp/simplesamlphp/commit/b1af4e47c81bca2bee633b3f84f4fde624f359ba
- https://github.com/simplesamlphp/simplesamlphp/commit/d26eb8f17dc9916a5ef2fd0a286b0fc96a561e71
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/simplesamlphp/201606-01.yaml
- https://github.com/simplesamlphp/simplesamlphp
- https://simplesamlphp.org/security/201606-01
