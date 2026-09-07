# [M] Silverstripe CSRF vulnerability in GridFieldAddExistingAutocompleter

## Summary
Severity: Medium
Advisory: GHSA-2hpc-mf4q-j885
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-2hpc-mf4q-j885
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <3.1.17
- Packagist: `silverstripe/framework` — affected >=3.2.0 <3.2.2
- Packagist: `silverstripe/framework` — affected >=3.3.0-beta1 <3.3.0

## Details
GridField does not have sufficient CSRF protection, meaning that in some cases users with CMS access can be tricked into posting unspecified data into the CMS from external websites. Amongst other default CMS interfaces, GridField is used for management of groups, users and permissions in the CMS.

The resolution for this issue is to ensure that all gridFieldAlterAction submissions are checked for the SecurityID token during submission.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/013524af5069bb0cf909853f04418d9bef56d18c
- https://github.com/silverstripe/silverstripe-framework/commit/56e92f5a32e45849cc9361c8603c31d7010c9d36
- https://github.com/silverstripe/silverstripe-framework/commit/e2c77c5a8f13e901c51a3684210811559b592f0c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2016-002-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2016-002
