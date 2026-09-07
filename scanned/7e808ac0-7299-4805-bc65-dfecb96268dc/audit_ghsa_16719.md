# [M] Silverstripe External redirection risk in Security?ReturnURL

## Summary
Severity: Medium
Advisory: GHSA-vp8p-c6xj-xpj7
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-vp8p-c6xj-xpj7
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <3.0.14
- Packagist: `silverstripe/framework` — affected >=3.1.0 <3.1.13

## Details
A vulnerability has been found in the SilverStripe framework where a login url can be potentially redirected to an external site.

For example, the url http://www.my-silverstripe-site.com/Security/login?BackURL=/\attacker-site.com will redirect successful logins to the page http://attacker-site.com. If that website were set up to look identical to the first with "login failed" then the user will likely just enter their user/pass again.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/22a35e48a9f513d4caa3b4e9b8dd21c49ffc8f2c
- https://github.com/silverstripe/silverstripe-framework/commit/c14e7f6b764ae4646461f3fc3a46452fdaa9e02a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2015-012-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/software/download/security-releases/ss-2015-012
