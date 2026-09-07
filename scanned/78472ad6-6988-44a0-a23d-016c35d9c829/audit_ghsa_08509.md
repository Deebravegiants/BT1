# [M] Cockpit CMS: Stored cross-site scripting vulnerability in the Set field type's Display template option

## Summary
Severity: Medium
Advisory: GHSA-ch4j-vcf5-58x5
CVE: CVE-2026-23695
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-ch4j-vcf5-58x5
Type: github-advisory

## Affected
- Packagist: `cockpit-hq/cockpit` — affected >=0

## Details
Cockpit CMS through version 2.14.0, patched in commit 72a83fc, contains a stored cross-site scripting vulnerability in the Set field type's Display template option, where the template string is processed by the $interpolate function using new Function() and rendered via Vue's v-html directive without sanitization. An attacker with content/:models/manage permission can inject arbitrary JavaScript into the Display template, which executes in the browser of any user viewing the collection items list.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-23695
- https://github.com/Cockpit-HQ/Cockpit/commit/72a83fcfe85ad8330e9ae834bc02fa517b5749e9
- https://github.com/Cockpit-HQ/Cockpit
- https://www.vulncheck.com/advisories/cockpit-cms-stored-xss-via-set-field-display-template
