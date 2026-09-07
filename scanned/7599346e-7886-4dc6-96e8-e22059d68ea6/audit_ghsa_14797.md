# [C] Arbitrary Code Execution in TYPO3 CMS

## Summary
Severity: Critical
Advisory: GHSA-67wg-6j7r-mqh8
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-67wg-6j7r-mqh8
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.22
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.5

## Details
Due to a missing file extension in the fileDenyPattern, backend user are allowed to upload *.pht files which can be executed in certain web server setups. The new default fileDenyPattern is the following, which might have been overridden in the TYPO3 Install Tool.
```
\.(php[3-7]?|phpsh|phtml|pht)(\..*)?$|^\.htaccess$
```

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2017-09-05-4.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2017-007
