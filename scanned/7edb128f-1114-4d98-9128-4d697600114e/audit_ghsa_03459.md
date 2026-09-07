# [M] Cross-Site Scripting in Bootstrap Package

## Summary
Severity: Medium
Advisory: GHSA-p48w-vf3c-rqjx
CVE: CVE-2021-21365
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-29
Source: https://github.com/advisories/GHSA-p48w-vf3c-rqjx
Type: github-advisory

## Affected
- Packagist: `bk2k/bootstrap-package` — affected >=7.1.0 <7.1.2
- Packagist: `bk2k/bootstrap-package` — affected >=8.0.0 <8.0.8
- Packagist: `bk2k/bootstrap-package` — affected >=9.0.0 <9.0.4
- Packagist: `bk2k/bootstrap-package` — affected >=9.1.0 <9.1.3
- Packagist: `bk2k/bootstrap-package` — affected >=10.0.0 <10.0.10
- Packagist: `bk2k/bootstrap-package` — affected >=11.0.0 <11.0.3

## Details
### Problem
It has been discovered that rendering content in the website frontend is vulnerable to cross-site scripting. A valid backend user account is needed to exploit this vulnerability.

The following templates are affected by the vulnerability:

* `Resources/Private/Partials/ContentElements/Carousel/Item/CallToAction.html`
* `Resources/Private/Partials/ContentElements/Carousel/Item/Header.html`
* `Resources/Private/Partials/ContentElements/Carousel/Item/Text.html`
* `Resources/Private/Partials/ContentElements/Carousel/Item/TextAndImage.html`
* `Resources/Private/Partials/ContentElements/Header/SubHeader.html`

Users of the extension, who have overwritten  the affected templates with custom code must manually apply the security fix as shown in [this Git commit](https://github.com/benjaminkott/bootstrap_package/commit/de3a568fc311d6712d9339643e51e8627c80530b).

### Solution
Update to version 7.1.2, 8.0.8, 9.0.4, 9.1.3, 10.0.10 or 11.0.3 of the Bootstrap Package that fix the problem described.

Updated version are available from the TYPO3 extension manager, Packagist and at https://extensions.typo3.org/extension/download/bootstrap_package/.

### Credits
Thanks to TYPO3 security team member Oliver Hader who reported and fixed the issue.

## References
- https://github.com/benjaminkott/bootstrap_package/security/advisories/GHSA-p48w-vf3c-rqjx
- https://nvd.nist.gov/vuln/detail/CVE-2021-21365
- https://github.com/benjaminkott/bootstrap_package/commit/de3a568fc311d6712d9339643e51e8627c80530b
- https://typo3.org/security/advisory/typo3-ext-sa-2021-007
