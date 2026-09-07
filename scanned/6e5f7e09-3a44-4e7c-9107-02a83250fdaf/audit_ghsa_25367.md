# [H] TYPO3 Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-fh4q-hxrw-cjqq
CVE: CVE-2017-14251
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-fh4q-hxrw-cjqq
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.22
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.5

## Details
Unrestricted File Upload vulnerability in the fileDenyPattern in sysext/core/Classes/Core/SystemEnvironmentBuilder.php in TYPO3 7.6.0 to 7.6.21 and 8.0.0 to 8.7.4 allows remote authenticated users to upload files with a .pht extension and consequently execute arbitrary PHP code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14251
- https://github.com/TYPO3/typo3
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2017-007
- http://blog.emaze.net/2017/12/typo3-unrestricted-file-upload-remote.html
- http://www.securityfocus.com/bid/100620
- http://www.securitytracker.com/id/1039295
