# [M] Typo3 Broken Access Control in Import Module

## Summary
Severity: Medium
Advisory: GHSA-f5rr-9r84-wwqf
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-f5rr-9r84-wwqf
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.8

## Details
It has been discovered that the Import/Export module is susceptible to broken access control. Regular backend users have access to import functionality which usually only is available to admin users or users having User TSconfig setting options.impexp.enableImportForNonAdminUser explicitly enabled.

Database content to be imported however was correctly checked against users’ permissions and not affected. However it was possible to upload files by-passing restrictions of the file abstraction layer (FAL) - however this did not affect executable files which have been correctly secured by fileDenyPattern.

Currently the only known vulnerability is to directly inject *.form.yaml files which could be used to trigger the vulnerability of TYPO3-CORE-SA-2018-003 (privilege escalation & SQL injection) - which requires the Form Framework (ext:form) being available on an according website. CVSSv3 scoring is based on this scenario.

A valid backend user account is needed in order to exploit this vulnerability.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-06-25-7.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2019-017
