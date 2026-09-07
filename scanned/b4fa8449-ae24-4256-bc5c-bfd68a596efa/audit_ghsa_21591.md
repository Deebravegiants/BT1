# [M] Reflected XSS in querystring parameters

## Summary
Severity: Medium
Advisory: GHSA-vvxf-r4vm-2vm6
CVE: CVE-2022-38462
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-vvxf-r4vm-2vm6
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.0 <4.11.13

## Details
An attacker could inject a XSS payload in a Silverstripe CMS response by carefully crafting a return URL on a /dev/build or /Security/login request.

To exploit this vulnerability, an attacker would need to convince a user to follow a link with a malicious payload.

This will only affect projects configured to output PHP warnings to the browser. By default, Silverstripe CMS will only output PHP warnings if your SS_ENVIRONMENT_TYPE environment variable is set to dev. Production sites should always set SS_ENVIRONMENT_TYPE to live.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38462
- https://forum.silverstripe.org/c/releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2022-38462.yaml
- https://www.silverstripe.org/blog/tag/release
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/cve-2022-38462
