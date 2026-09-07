# [M] Improper permissions handling in MediaWiki AbuseFilter

## Summary
Severity: Medium
Advisory: GHSA-rmcp-9fhq-58pv
CVE: CVE-2024-47913
CWE: CWE-532
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-10-05
Source: https://github.com/advisories/GHSA-rmcp-9fhq-58pv
Type: github-advisory

## Affected
- Packagist: `mediawiki/abuse-filter` — affected >=0 <1.39.9
- Packagist: `mediawiki/abuse-filter` — affected >=1.40.0 <1.41.3
- Packagist: `mediawiki/abuse-filter` — affected >=1.42.0 <1.42.2

## Details
An issue was discovered in the AbuseFilter extension for MediaWiki before 1.39.9, 1.40.x and 1.41.x before 1.41.3, and 1.42.x before 1.42.2. An API caller can match a filter condition against AbuseFilter logs even if the caller is not authorized to view the log details for the filter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-47913
- https://gerrit.wikimedia.org/r/c/mediawiki/extensions/AbuseFilter/+/1076855
- https://github.com/wikimedia/mediawiki-extensions-AbuseFilter
- https://phabricator.wikimedia.org/T372998
