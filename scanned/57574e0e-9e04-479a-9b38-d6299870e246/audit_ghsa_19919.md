# [M] Concrete CMS affected by a stored XSS in Folder Function.The "Add Folder" functionality

## Summary
Severity: Medium
Advisory: GHSA-pvmx-mjmh-jfcx
CVE: CVE-2025-0660
CWE: CWE-20, CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2025-03-10
Source: https://github.com/advisories/GHSA-pvmx-mjmh-jfcx
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.4.0RC1

## Details
Concrete CMS versions 9.0.0 through 9.3.9 are affected by a stored XSS in Folder Function.The "Add Folder" functionality lacks input sanitization, allowing a rogue admin to inject XSS payloads as folder names.  The Concrete CMS security team gave this vulnerability a CVSS 4.0 Score of 4.8 with vector: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N. Versions below 9 are not affected. Thanks, Alfin Joseph for reporting.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-0660
- https://github.com/concretecms/bedrock/pull/370
- https://github.com/concretecms/concretecms/pull/12454
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/940-release-notes
- https://github.com/concretecms/concretecms
