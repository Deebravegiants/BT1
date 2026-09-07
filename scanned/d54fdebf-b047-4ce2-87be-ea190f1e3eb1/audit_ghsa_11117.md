# [H] MantisBT Vulnerable to Stored HTML Injection in Tag Delete Confirmation

## Summary
Severity: High
Advisory: GHSA-fh48-f69w-7vmp
CVE: CVE-2026-33517
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-fh48-f69w-7vmp
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=2.28.0 <2.28.1

## Details
Improper escaping of Tag name when deleting it in tag_delete.php allows an attacker to inject HTML and, if CSP settings permit, achieve execution of arbitrary JavaScript.

### Impact
Cross-site scripting (XSS).

### Patches
80990f43153167c73f11eb4b2bc7108d0c3d6b46

### Workarounds
* Revert commit d6890320752ecf37bd74d11fe14fe7dc12335be9
* Manually edit language files to remove the sprintf placeholder `%1$s` from *$s_tag_delete_message*  string, for example with `sed -r -i '/tag_delete_message/s/.%1\$s.//' -- lang/`

### Credits
MantisBT hanks Vishal Shukla for discovering and responsibly reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-fh48-f69w-7vmp
- https://nvd.nist.gov/vuln/detail/CVE-2026-33517
- https://github.com/mantisbt/mantisbt/commit/80990f43153167c73f11eb4b2bc7108d0c3d6b46
- https://github.com/mantisbt/mantisbt/commit/d6890320752ecf37bd74d11fe14fe7dc12335be9
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=36971
