# [M] SilverStripe Versioned Files module Unpublished files are exposed publicly

## Summary
Severity: Medium
Advisory: GHSA-xm6j-x342-gwq9
CVE: CVE-2019-16409
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-11-12
Source: https://github.com/advisories/GHSA-xm6j-x342-gwq9
Type: github-advisory

## Affected
- Packagist: `symbiote/silverstripe-versionedfiles` — affected >=0
- Packagist: `silverstripe/framework` — affected >=4.0.0 <4.3.5
- Packagist: `silverstripe/framework` — affected >=4.4.0 <4.4.4

## Details
In the Versioned Files module through 2.0.3 for SilverStripe 3.x, unpublished versions of files are publicly exposed to anyone who can guess their URL. This guess could be highly informed by a basic understanding of the symbiote/silverstripe-versionedfiles source code. (Users who upgrade from SilverStripe 3.x to 4.x and had Versioned Files installed have no further need for this module, because the 4.x release has built-in versioning. However, nothing in the upgrade process automates the destruction of these insecure artefacts, nor alerts the user to the criticality of destruction.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16409
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2019-16409.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://github.com/symbiote/silverstripe-versionedfiles
- https://www.silverstripe.org/download/security-releases/cve-2019-16409
