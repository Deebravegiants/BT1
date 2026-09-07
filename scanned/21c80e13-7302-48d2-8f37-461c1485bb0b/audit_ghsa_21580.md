# [M] Stored XSS in Compare Mode

## Summary
Severity: Medium
Advisory: GHSA-66jf-xm2m-7m8r
CVE: CVE-2022-38145
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-22
Source: https://github.com/advisories/GHSA-66jf-xm2m-7m8r
Type: github-advisory

## Affected
- Packagist: `silverstripe/versioned-admin` — affected >=1.0.0 <1.11.1

## Details
A malicious content author could add a Javascript payload to a page's meta description and get it executed in the versioned history compare view.

This vulnerability requires access to the CMS to be deployed. The attacker must then convince a privileged user to access the version history for that page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38145
- https://forum.silverstripe.org/c/releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/versioned-admin/CVE-2022-38145.yaml
- https://www.silverstripe.org/blog/tag/release
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/cve-2022-38145
