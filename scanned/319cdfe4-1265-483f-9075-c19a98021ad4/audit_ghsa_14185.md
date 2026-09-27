# [M] phpMyFAQ Improper Access Control vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r69v-q48g-3966
CVE: CVE-2023-2429
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2023-04-30
Source: https://github.com/advisories/GHSA-r69v-q48g-3966
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <3.1.13

## Details
phpMyFAQ prior to version 3.1.13 does not properly validate email addresses when updating user profiles. This vulnerability allows an attacker to manipulate their email address and change it to another email address that is already registered in the system, including email addresses belonging to other users such as the administrator. Once the attacker has control of the other user's email address, they can request to remove the user from the system, leading to a loss of data and access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2429
- https://github.com/thorsten/phpmyfaq/commit/07552f5577ff8b1e6f7cdefafcce9b2a744d3a24
- https://github.com/thorsten/phpmyfaq
- https://huntr.com/bounties/20d3a0b3-2693-4bf1-b196-10741201a540
- https://huntr.dev/bounties/20d3a0b3-2693-4bf1-b196-10741201a540
