# [M] SocialNetwork Cross-Site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3fm8-7gpf-p8fm
CVE: CVE-2017-7390
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-3fm8-7gpf-p8fm
Type: github-advisory

## Affected
- Packagist: `movingbytes/social-network` — affected >=0

## Details
A Cross-Site Scripting (XSS) was discovered in 'SocialNetwork v1.2.1'. The vulnerability exists due to insufficient filtration of user-supplied data (mail) passed to the 'SocialNetwork-andrea/app/template/pw_forgot.php' URL. An attacker could execute arbitrary HTML and script code in a browser in the context of the vulnerable website.
A patch for the vulnerability is available at https://github.com/andreas83/SocialNetwork/commit/1b0799d08fda2f3099beaae1234b8b468deb8db1

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7390
- https://github.com/andreas83/SocialNetwork/issues/84
- https://github.com/andreas83/SocialNetwork/commit/1b0799d08fda2f3099beaae1234b8b468deb8db1
- https://github.com/andreas83/SocialNetwork
- http://www.securityfocus.com/bid/97312
