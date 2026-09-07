# [M] Silverstripe XSS in shortcodes

## Summary
Severity: Medium
Advisory: GHSA-9cx2-hj6m-fv58
CVE: CVE-2022-38724
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-9cx2-hj6m-fv58
Type: github-advisory

## Affected
- Packagist: `silverstripe/assets` — affected >=1.0.0 <1.11.1
- Packagist: `silverstripe/framework` — affected >=4.0.0 <4.11.13

## Details
A malicious content author could add arbitrary attributes to HTML editor shortcodes which could be used to inject a JavaScript payload on the front end of the site. The shortcode providers that ship with Silverstripe CMS have been reviewed and attribute whitelists have been implemented where appropriate to negate this risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38724
- https://forum.silverstripe.org/c/releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/assets/CVE-2022-38724.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2022-38724.yaml
- https://www.silverstripe.org/blog/tag/release
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/cve-2022-38724
