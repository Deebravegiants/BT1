# [M] auditor-bundle vulnerable to Cross-site Scripting because name of entity does not get escaped

## Summary
Severity: Medium
Advisory: GHSA-78vg-7v27-hj67
CVE: CVE-2024-45592
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2024-09-10
Source: https://github.com/advisories/GHSA-78vg-7v27-hj67
Type: github-advisory

## Affected
- Packagist: `damienharper/auditor-bundle` — affected >=0 <5.2.6

## Details
### Summary
Unescaped entity property enables Javascript injection.

### Details
I think this is possible because %source_label% in twig macro is not escaped. Therefore script tags can be inserted and are executed.

### PoC
- clone example project https://github.com/DamienHarper/auditor-bundle-demo
- create author with FullName <script>alert()</script>
- delete author
- view audit of authors
- alert is displayed

### Impact
persistent XSS. JS can be injected and executed.

## References
- https://github.com/DamienHarper/auditor-bundle/security/advisories/GHSA-78vg-7v27-hj67
- https://nvd.nist.gov/vuln/detail/CVE-2024-45592
- https://github.com/DamienHarper/auditor-bundle/commit/42ba2940d8b99467de0c806ea5655cc1c6882cd1
- https://github.com/DamienHarper/auditor-bundle/commit/e7deb377fa89677d44973b486d26d6a7374233ae
- https://github.com/DamienHarper/auditor-bundle
