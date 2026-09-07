# [M] MantisBT is Vulnerable to Reflected XSS in Rendering Dynamic Custom Textarea Field

## Summary
Severity: Medium
Advisory: GHSA-j7v9-f46r-2rp4
CVE: CVE-2026-41897
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-j7v9-f46r-2rp4
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=1.0.0 <2.28.2

## Details
Lack of validation of filter_target parameter on return_dynamic_filters.php (normally used as an AJAX in View Issues Page) allows an attacker to inject arbitrary HTML if the target is a TEXTAREA custom field.

### Impact
Cross-site scripting (XSS)

### Patches
- c885af13f0b8596714ffe11df757c09f35fbd8f4

### Workarounds
None

### Credits

Thanks to siunam (Tang Cheuk Hei) for discovering and responsibly reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-j7v9-f46r-2rp4
- https://nvd.nist.gov/vuln/detail/CVE-2026-41897
- https://github.com/mantisbt/mantisbt/commit/c885af13f0b8596714ffe11df757c09f35fbd8f4
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37013
