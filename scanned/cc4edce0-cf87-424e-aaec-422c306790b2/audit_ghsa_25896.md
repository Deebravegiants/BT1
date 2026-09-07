# [M] Path Disclosure within joomla/filesystem class

## Summary
Severity: Medium
Advisory: GHSA-rc8q-45v8-x6xc
CVE: CVE-2022-23794
CWE: CWE-209
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-03-31
Source: https://github.com/advisories/GHSA-rc8q-45v8-x6xc
Type: github-advisory

## Affected
- Packagist: `joomla/filesystem` — affected >=0 <1.6.2
- Packagist: `joomla/filesystem` — affected >=2.0.0 <2.0.1

## Details
An issue was discovered in Joomla! 3.0.0 through 3.10.6 & 4.0.0 through 4.1.0. Uploading a file name of an excess length causes the error. This error brings up the screen with the path of the source code of the web application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23794
- https://developer.joomla.org/security-centre/871-20220302-core-path-disclosure-within-filesystem-error-messages.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/joomla/filesystem/CVE-2022-23794.yaml
- https://github.com/joomla-framework/filesystem
