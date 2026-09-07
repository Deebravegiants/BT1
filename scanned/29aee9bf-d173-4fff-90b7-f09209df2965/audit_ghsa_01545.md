# [M] Cross-site Scripting vulnerability in Kitodo.Presentation

## Summary
Severity: Medium
Advisory: GHSA-fpqv-x9hm-35j9
CVE: CVE-2020-16095
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-07-31
Source: https://github.com/advisories/GHSA-fpqv-x9hm-35j9
Type: github-advisory

## Affected
- Packagist: `kitodo/presentation` — affected >=0 <3.1.2

## Details
### Impact
Kitodo.Presentation fails to properly encode URL parameters for output in HTML making it vulnerable to Cross Site Scripting (XSS). Only sites using the `ListView`, `Navigation` or `PageView` plugins are affected.

It also includes jQuery 3.4.1 which is known to be vulnerable against Cross Site Scripting, although there is currently no known way to exploit this in Kitodo.Presentation.

### Patches
An updated version of Kitodo.Presentation is available on [GitHub](https://github.com/kitodo/kitodo-presentation/releases/tag/v3.1.2), [Packagist](https://packagist.org/packages/kitodo/presentation#v3.1.2) and in the [TYPO3 Extension Repository](https://extensions.typo3.org/extension/dlf/). Users are advised to update as soon as possible.

The issue was also fixed in release 2.3.1 of the 2.x branch, although it is generally not recommended to run this branch since it depends on an outdated TYPO3 version.

### References
TYPO3 Security Advisory [TYPO3-EXT-SA-2020-015](https://typo3.org/security/advisory/typo3-ext-sa-2020-015)
jQuery Security Advisory [GHSA-gxr4-xjj5-5px2](https://github.com/jquery/jquery/security/advisories/GHSA-gxr4-xjj5-5px2)
Open Bug Bounty Report [OBB-1219978](https://www.openbugbounty.org/reports/1219978/)

### Contact
If you have any questions or comments about this advisory:
* [Open an issue](https://github.com/kitodo/kitodo-presentation/issues/new/choose)
* Email us at [security@kitodo.org](mailto:security@kitodo.org)

## References
- https://github.com/kitodo/kitodo-presentation/security/advisories/GHSA-fpqv-x9hm-35j9
- https://nvd.nist.gov/vuln/detail/CVE-2020-16095
- https://github.com/kitodo/kitodo-presentation/commit/6a67256388350cc69efa7f36bbaee50c919ca23c
- https://github.com/kitodo/kitodo-presentation
- https://typo3.org/help/security-advisories
- https://typo3.org/security/advisory/typo3-ext-sa-2020-015
