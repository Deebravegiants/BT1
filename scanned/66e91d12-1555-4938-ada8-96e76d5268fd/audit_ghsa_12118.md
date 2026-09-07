# [M] Statamic has Reflected XSS via unescaped redirect parameter in its password reset form tag

## Summary
Severity: Medium
Advisory: GHSA-3jg4-p23x-p4qx
CVE: CVE-2026-33883
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-3jg4-p23x-p4qx
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.73.16
- Packagist: `statamic/cms` — affected >=6.0.0-alpha.1 <6.7.2

## Details
### Impact

The `user:reset_password_form` tag could render user-input directly into HTML without escaping, allowing an attacker to craft a URL that executes arbitrary JavaScript in the victim's browser.

### Patches

This has been fixed in 5.73.16 and 6.7.2.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-3jg4-p23x-p4qx
- https://nvd.nist.gov/vuln/detail/CVE-2026-33883
- https://github.com/statamic/cms
