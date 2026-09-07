# [H] MantisBT has Stored XSS on Move Attachments Admin Page

## Summary
Severity: High
Advisory: GHSA-7mqj-8gj2-cg59
CVE: CVE-2026-44655
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-7mqj-8gj2-cg59
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=1.3.0 <2.28.2

## Details
Unescaped Project Name allows an attacker that can set it (which typically requires manager or administrator access level) to inject HTML in Move Attachments admin page.

### Impact
Cross-site scripting (XSS).
This is mitigated by Content Security Policy which restricts scripts execution.

### Patches
- 5cb4b469295889f5d2b01677c9bf82c143e0fdaa

### Workarounds
None

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-7mqj-8gj2-cg59
- https://nvd.nist.gov/vuln/detail/CVE-2026-44655
- https://github.com/mantisbt/mantisbt/commit/5cb4b469295889f5d2b01677c9bf82c143e0fdaa
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37099
