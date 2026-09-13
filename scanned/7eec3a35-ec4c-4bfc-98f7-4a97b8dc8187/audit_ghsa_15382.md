# [H] Persistent Cross-site Scripting in Ibexa RichText Field Type

## Summary
Severity: High
Advisory: GHSA-hvcf-6324-cjh7
CVE: CVE-2024-43369
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-14
Source: https://github.com/advisories/GHSA-hvcf-6324-cjh7
Type: github-advisory

## Affected
- Packagist: `ibexa/fieldtype-richtext` — affected >=4.6.0 <4.6.10

## Details
### Impact
The validator for the RichText fieldtype blocklists `javascript:` and `vbscript:` in links to prevent XSS. This can leave other options open, and the check can be circumvented using upper case. Content editing permissions for RichText content is required to exploit this vulnerability, which typically means Editor role or higher. The fix implements an allowlist instead, which allows only approved link protocols. The new check is case insensitive.

### Patches
- See "Patched versions".
- https://github.com/ibexa/fieldtype-richtext/commit/59e9c1a9da60597f60cf7338bf289dccaa7e27ca (and follow-up https://github.com/ibexa/fieldtype-richtext/commit/0a3b830e8806d5169f697351fdc48ffd95a25c67)

### Workarounds
None.

### References
- Same issue in v3.3: https://github.com/ezsystems/ezplatform-richtext/security/advisories/GHSA-rhm7-7469-rcpw
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
- https://github.com/ibexa/fieldtype-richtext/commit/0a3b830e8806d5169f697351fdc48ffd95a25c67
- https://github.com/ibexa/fieldtype-richtext/commit/59e9c1a9da60597f60cf7338bf289dccaa7e27ca
- https://developers.ibexa.co/security-advisories/ibexa-sa-2024-005-persistent-xss-in-richtext
- https://github.com/ibexa/fieldtype-richtext
