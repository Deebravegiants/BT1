# [H] Persistent Cross-site Scripting in eZ Platform Rich Text Field Type

## Summary
Severity: High
Advisory: GHSA-rhm7-7469-rcpw
CVE: CVE-2024-43372
CWE: CWE-79
Ecosystem: Packagist
Published: 2024-08-14
Source: https://github.com/advisories/GHSA-rhm7-7469-rcpw
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-richtext` — affected >=3.3.0 <3.3.40

## Details
### Impact
The validator for the RichText fieldtype blocklists `javascript:` and `vbscript:` in links to prevent XSS. This can leave other options open, and the check can be circumvented using upper case. Content editing permissions for RichText content is required to exploit this vulnerability, which typically means Editor role or higher. The fix implements an allowlist instead, which allows only approved link protocols. The new check is case insensitive.

### Patches
- See "Patched versions".
- https://github.com/ezsystems/ezplatform-richtext/commit/6131975108fa9756e17043e7a06a4e72f786f842 (and follow-ups https://github.com/ezsystems/ezplatform-richtext/commit/8b75c603dfd1ad6f6f3db15ae2324876683cbaf9 and https://github.com/ezsystems/ezplatform-richtext/commit/7bbc6d024c6146d1e1ba84d27a3ebffe9459613e and https://github.com/ezsystems/ezplatform-richtext/commit/2c652915625c47b493a2be06924f4c87d1df7d8e and https://github.com/ezsystems/ezplatform-richtext/commit/dbe816f3ff4c903cc508dfdcdca8791c8284d292)

### Workarounds
None.

### References
- Same issue in v4.6: https://github.com/ibexa/fieldtype-richtext/security/advisories/GHSA-hvcf-6324-cjh7
- Ibexa advisory: https://developers.ibexa.co/security-advisories/ibexa-sa-2024-005-persistent-xss-in-richtext

### Credit
This vulnerability was discovered and reported to Ibexa by Alec Romano: https://github.com/4rdr
We thank them for reporting it responsibly to us.

How to report security issues:
https://doc.ibexa.co/en/latest/infrastructure_and_maintenance/security/reporting_issues/

## References
- https://github.com/ezsystems/ezplatform-richtext/security/advisories/GHSA-rhm7-7469-rcpw
- https://github.com/ibexa/fieldtype-richtext/security/advisories/GHSA-hvcf-6324-cjh7
- https://nvd.nist.gov/vuln/detail/CVE-2024-43369
- https://github.com/ezsystems/ezplatform-richtext/commit/2c652915625c47b493a2be06924f4c87d1df7d8e
- https://github.com/ezsystems/ezplatform-richtext/commit/6131975108fa9756e17043e7a06a4e72f786f842
- https://github.com/ezsystems/ezplatform-richtext/commit/7bbc6d024c6146d1e1ba84d27a3ebffe9459613e
- https://github.com/ezsystems/ezplatform-richtext/commit/8b75c603dfd1ad6f6f3db15ae2324876683cbaf9
- https://github.com/ezsystems/ezplatform-richtext/commit/dbe816f3ff4c903cc508dfdcdca8791c8284d292
- https://developers.ibexa.co/security-advisories/ibexa-sa-2024-005-persistent-xss-in-richtext
- https://github.com/ezsystems/ezplatform-richtext
