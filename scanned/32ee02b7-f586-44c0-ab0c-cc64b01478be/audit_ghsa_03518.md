# [M] XSS in CreateQueuedJobTask

## Summary
Severity: Medium
Advisory: GHSA-xgpf-p52j-pf7m
CVE: CVE-2021-27938
CWE: CWE-79
Ecosystem: Packagist
Published: 2021-03-24
Source: https://github.com/advisories/GHSA-xgpf-p52j-pf7m
Type: github-advisory

## Affected
- Packagist: `symbiote/silverstripe-queuedjobs` — affected >=3.0.0 <3.0.2
- Packagist: `symbiote/silverstripe-queuedjobs` — affected >=3.1.0 <3.1.4
- Packagist: `symbiote/silverstripe-queuedjobs` — affected >=4.0.0 <4.0.7
- Packagist: `symbiote/silverstripe-queuedjobs` — affected >=4.1.0 <4.1.2
- Packagist: `symbiote/silverstripe-queuedjobs` — affected >=4.2.0 <4.2.4
- Packagist: `symbiote/silverstripe-queuedjobs` — affected >=4.3.0 <4.3.3
- Packagist: `symbiote/silverstripe-queuedjobs` — affected >=4.4.0 <4.4.3
- Packagist: `symbiote/silverstripe-queuedjobs` — affected >=4.5.0 <4.5.1
- Packagist: `symbiote/silverstripe-queuedjobs` — affected >=4.6.0 <4.6.4

## Details
A vulnerability has been identified in the Silverstripe CMS 3 and 4 version of the symbiote/silverstripe-queuedjobs module. A Cross Site Scripting vulnerability allows an attacker to inject an arbitrary payload in the CreateQueuedJobTask dev task via a specially crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27938
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symbiote/silverstripe-queuedjobs/CVE-2021-27938.yaml
- https://github.com/symbiote/silverstripe-queuedjobs/releases
- https://www.silverstripe.org/download/security-releases/cve-2021-27938
