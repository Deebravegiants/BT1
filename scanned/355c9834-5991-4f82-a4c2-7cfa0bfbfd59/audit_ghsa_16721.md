# [M] silverstripe/framework has Cross-site Scripting vulnerability in RedirectorPage

## Summary
Severity: Medium
Advisory: GHSA-pp7q-6j3f-74vj
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-pp7q-6j3f-74vj
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.4.0-rc1 <3.4.6
- Packagist: `silverstripe/framework` — affected >=3.5.0-rc1 <3.5.4

## Details
RedirectorPage will allow users to specify a non-url malicious script as the redirection path without validation. Users which follow this url may allow this script to execute within their browser.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2017-003-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2017-003
