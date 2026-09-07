# [M] Stored XSS in link tags added via XHR in SilverStripe Framework

## Summary
Severity: Medium
Advisory: GHSA-rppc-655v-7j3c
CVE: CVE-2022-28803
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-06-29
Source: https://github.com/advisories/GHSA-rppc-655v-7j3c
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.0 <4.10.9

## Details
SilverStripe Framework 4.x prior to 4.10.9 is vulnerable to cross-site scripting inside the href attribute of an HTML hyperlink, which can be added to website content via XMLHttpRequest (XHR) by an authenticated CMS user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28803
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2022-28803.yaml
- https://www.silverstripe.org/download/security-releases/cve-2022-28803
