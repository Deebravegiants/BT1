# [M] MantisBT XSS in manage_custom_field_update.php

## Summary
Severity: Medium
Advisory: GHSA-cvrm-cr3m-qj92
CVE: CVE-2020-35571
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cvrm-cr3m-qj92
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.25.0

## Details
An issue was discovered in MantisBT through 2.24.3. In the helper_ensure_confirmed call in manage_custom_field_update.php, the custom field name is not sanitized. This may be problematic depending on CSP settings.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35571
- https://github.com/mantisbt/mantisbt/commit/100c3d58c3f6f12b7a6cf97fba473ede521f20db
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=27768
