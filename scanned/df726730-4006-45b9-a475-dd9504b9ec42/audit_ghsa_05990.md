# [H] silverstripe-advancedworkflow vulnerable to remote code execution via advanced workflow email template

## Summary
Severity: High
Advisory: GHSA-39mm-rwm3-29jp
CVE: CVE-2026-54718
CWE: CWE-20, CWE-1336
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-27
Source: https://github.com/advisories/GHSA-39mm-rwm3-29jp
Type: github-advisory

## Affected
- Packagist: `symbiote/silverstripe-advancedworkflow` — affected >=0 <6.4.5
- Packagist: `symbiote/silverstripe-advancedworkflow` — affected >=7.0.0 <7.1.3
- Packagist: `symbiote/silverstripe-advancedworkflow` — affected >=7.2.0 <7.2.1

## Details
### Impact
The advanced workflow email template field is vulnerable to a specially crafted payload that can be used to run arbitrary code on the server.

### Reported by
Steve Boyd
Silverstripe Ltd.

## References
- https://github.com/silverstripe/silverstripe-advancedworkflow/security/advisories/GHSA-39mm-rwm3-29jp
- https://github.com/silverstripe/silverstripe-advancedworkflow/pull/629
- https://github.com/silverstripe/silverstripe-advancedworkflow/pull/630
- https://github.com/silverstripe/silverstripe-advancedworkflow/commit/28d0b536491e5c68b1c445579bdd1ddc8beaf8bb
- https://github.com/silverstripe/silverstripe-advancedworkflow/commit/f170766af992ed2ed3e5f21d127d0d0d3129678b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symbiote/silverstripe-advancedworkflow/CVE-2026-54718.yaml
- https://github.com/silverstripe/silverstripe-advancedworkflow
- https://github.com/silverstripe/silverstripe-advancedworkflow/releases/tag/6.4.5
- https://github.com/silverstripe/silverstripe-advancedworkflow/releases/tag/7.1.3
- https://github.com/silverstripe/silverstripe-advancedworkflow/releases/tag/7.2.1
- https://www.silverstripe.org/download/security-releases/cve-2026-54718
