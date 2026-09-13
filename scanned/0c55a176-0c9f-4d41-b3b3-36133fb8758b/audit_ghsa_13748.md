# [M] OroCRMCallBundle has incorrect call view page visibility

## Summary
Severity: Medium
Advisory: GHSA-897w-jv7j-6r7g
CVE: CVE-2023-32063
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2023-11-27
Source: https://github.com/advisories/GHSA-897w-jv7j-6r7g
Type: github-advisory

## Affected
- Packagist: `oro/crm-call-bundle` — affected >=4.2.0
- Packagist: `oro/crm-call-bundle` — affected >=5.0.0 <5.0.4
- Packagist: `oro/crm-call-bundle` — affected >=5.1.0 <5.1.1

## Details
Back-office users can access information from any call event, bypassing ACL security restrictions due to insufficient security checks.

## References
- https://github.com/oroinc/crm/security/advisories/GHSA-897w-jv7j-6r7g
- https://nvd.nist.gov/vuln/detail/CVE-2023-32063
- https://github.com/oroinc/OroCRMCallBundle/commit/456b1dda7762abf4ff59eafffaa70ab7f09d1c85
- https://github.com/oroinc/OroCRMCallBundle/commit/9a41dff459bb4aff864175ca883d553ac0954950
- https://github.com/oroinc/crm
