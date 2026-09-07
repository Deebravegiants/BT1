# [M] Formie has XSS vulnerability for importing forms

## Summary
Severity: Medium
Advisory: GHSA-p9hh-mh5x-wvx3
CVE: CVE-2025-32427
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-04-11
Source: https://github.com/advisories/GHSA-p9hh-mh5x-wvx3
Type: github-advisory

## Affected
- Packagist: `verbb/formie` — affected >=0 <2.1.44

## Details
### Impact
When importing a form from JSON, if the field label or handle contained malicious content, the output wasn't correctly escaped when viewing a preview of what was to be imported.

As imports are undertaking primarily by users who have themselves exported the form from one environment to another, and would require direct manipulation of the JSON export, this is marked as moderate. This vulnerability will not occur unless someone deliberately tampers with the export.

### Patches
This has been fixed in Formie 2.1.44. Users should ensure they are running at least this version.

## References
- https://github.com/verbb/formie/security/advisories/GHSA-p9hh-mh5x-wvx3
- https://nvd.nist.gov/vuln/detail/CVE-2025-32427
- https://github.com/verbb/formie
