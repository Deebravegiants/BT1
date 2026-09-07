# [M] Concrete CMS has a stored Cross-site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-f4vq-pj32-gr4q
CVE: CVE-2026-3241
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-f4vq-pj32-gr4q
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.4.8

## Details
In Concrete CMS below version 9.4.8, a Cross-site Scripting (XSS) vulnerability exists in the "Legacy Form" block. An authenticated user with permissions to create or edit forms (e.g., a rogue administrator) can inject a persistent JavaScript payload into the options of a multiple-choice question (Checkbox List, Radio Buttons, or Select Box). This payload is then executed in the browser of any user who views the page containing the form. 

The Concrete CMS security team thanks M3dium for reporting.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3241
- https://github.com/concretecms/concretecms/pull/12826
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/948-release-notes
- https://github.com/concretecms/concretecms
