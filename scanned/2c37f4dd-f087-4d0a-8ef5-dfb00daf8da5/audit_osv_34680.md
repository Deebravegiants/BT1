# [M] CVE-2025-63693

## Summary
Severity: Medium
Advisory: CVE-2025-63693
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2025-11-18
Source: https://osv.dev/vulnerability/CVE-2025-63693
Type: osv

## Details
The comment editing template (dzz/comment/template/edit_form.htm) in DzzOffice 2.3.x lacks adequate security escaping for user-controllable data in multiple contexts, including HTML and JavaScript strings. This allows low-privilege attackers to construct comment content or request parameters and execute arbitrary JavaScript code when the victim opens the editing pop-up.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63693.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63693
- https://github.com/zyx0814/dzzoffice/issues/363
- https://github.com/Yohane-Mashiro/dzzoffice_xss
