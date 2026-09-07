# [H] Class destructors causing side-effects when being unserialized in TYPO3 CMS

## Summary
Severity: High
Advisory: GHSA-2rxh-h6h9-qrqc
CVE: CVE-2020-11066
CWE: CWE-1321, CWE-915
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2020-05-13
Source: https://github.com/advisories/GHSA-2rxh-h6h9-qrqc
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.17
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.2
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.2
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.17

## Details
Calling unserialize() on malicious user-submitted content can result in the following scenarios:
- trigger deletion of arbitrary directory in file system (if writable for web server)
- trigger message submission via email using identity of web site (mail relay)

Another insecure deserialization vulnerability is required to actually exploit mentioned aspects.

Update to TYPO3 versions 9.5.17 or 10.4.2 that fix the problem described.

### References
* https://typo3.org/security/advisory/typo3-core-sa-2020-004

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-2rxh-h6h9-qrqc
- https://nvd.nist.gov/vuln/detail/CVE-2020-11066
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2020-11066.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2020-11066.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2020-004
