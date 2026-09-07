# [M] Silverstripe Framework has a XSS in form messages

## Summary
Severity: Medium
Advisory: GHSA-ff6q-3c9c-6cf5
CVE: CVE-2024-53277
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-14
Source: https://github.com/advisories/GHSA-ff6q-3c9c-6cf5
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <5.3.8

## Details
In some cases, form messages can contain HTML markup. This is an intentional feature, allowing links and other relevant HTML markup for the given message.

Some form messages include content that the user can provide. There are scenarios in the CMS where that content doesn't get correctly sanitised prior to being included in the form message, resulting in an XSS vulnerability.

### References

- https://www.silverstripe.org/download/security-releases/cve-2024-53277

## Reported by

Leo Diamat from [Bastion Security Group](http://www.bastionsecurity.co.nz/)

## References
- https://github.com/silverstripe/silverstripe-framework/security/advisories/GHSA-ff6q-3c9c-6cf5
- https://nvd.nist.gov/vuln/detail/CVE-2024-53277
- https://github.com/silverstripe/silverstripe-framework/commit/74904f539347b7d1f8c5b5fb9e28d62ff251ee00
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2024-53277.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/cve-2024-53277
