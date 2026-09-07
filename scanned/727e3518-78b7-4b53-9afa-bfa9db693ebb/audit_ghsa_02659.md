# [H] XSS vulnerability on contacts view

## Summary
Severity: High
Advisory: GHSA-72hm-fx78-xwhc
CVE: CVE-2021-27911
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-72hm-fx78-xwhc
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=0 <3.3.4
- Packagist: `mautic/core` — affected >=4.0.0-alpha1 <4.0.0

## Details
### Impact
Mautic versions before 3.3.4/4.0.0 are vulnerable to an inline JS XSS attack through the contact's first or last name and triggered when viewing a contact's details page then clicking on the action drop down and hovering over the Campaigns button. Contact first and last name can be populated from different sources such as UI, API, 3rd party syncing, forms, etc. 

### Patches
Upgrade to 3.3.4 or 4.0.0

### Workarounds
No

### References
https://github.com/mautic/mautic/releases/tag/3.3.4
https://github.com/mautic/mautic/releases/tag/4.0.0

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-72hm-fx78-xwhc
- https://nvd.nist.gov/vuln/detail/CVE-2021-27911
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mautic/core/CVE-2021-27911.yaml
- https://github.com/mautic/mautic
