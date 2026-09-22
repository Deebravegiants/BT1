# [C]  Apostrophe CMS Insufficient Session Expiration vulnerability

## Summary
Severity: Critical
Advisory: GHSA-9j9m-8wjc-ff96
CVE: CVE-2021-25979
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-9j9m-8wjc-ff96
Type: github-advisory

## Affected
- npm: `apostrophe` — affected >=2.63.0 <3.4.0

## Details
Apostrophe CMS versions between 2.63.0 to 3.3.1 affected by an insufficient session expiration vulnerability, which allows unauthenticated remote attackers to hijack recently logged-in users' sessions. As a mitigation for older releases the user account in question can be archived (3.x) or moved to the trash (2.x and earlier) which does disable the existing session.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25979
- https://github.com/apostrophecms/apostrophe/commit/c211b211f9f4303a77a307cf41aac9b4ef8d2c7c
- https://github.com/apostrophecms/apostrophe
