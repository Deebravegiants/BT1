# [M] Sharp user-provided input can be evaluated in a SharpShowTextField with Vue template syntax

## Summary
Severity: Medium
Advisory: GHSA-9f58-4465-23c7
CVE: CVE-2025-62798
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-9f58-4465-23c7
Type: github-advisory

## Affected
- Packagist: `code16/sharp` — affected >=0 <9.11.1

## Details
A Cross-Site Scripting (XSS) vulnerability was discovered in code16/sharp when rendering content using the SharpShowTextField component.

In affected versions, expressions wrapped in `{{` & `}}` were evaluated by Vue. This allowed attackers to inject arbitrary JavaScript or HTML that executes in the browser when the field is displayed.

For example, if a field’s value contains `{{ Math.random() }}`, it will be executed instead of being displayed as text.

### Impact

Attackers who can control content rendered through SharpShowTextField could execute arbitrary JavaScript in the context of an authenticated user’s browser.

This could lead to:

- Theft of user session tokens.
- Unauthorized actions performed on behalf of users.
- Injection of malicious content into the admin panel.

### Patches

The issue has been fixed in v9.11.1 of code16/sharp package.

### Mitigation / Workarounds

Sanitize or encode any user-provided data that may include (`{{` & `}}`) before displaying it in a SharpShowTextField.

## References
- https://github.com/code16/sharp/security/advisories/GHSA-9f58-4465-23c7
- https://nvd.nist.gov/vuln/detail/CVE-2025-62798
- https://github.com/code16/sharp/pull/654
- https://github.com/ViktorMares/vue-js-xss-payload-list
- https://github.com/code16/sharp
- https://github.com/code16/sharp/releases/tag/v9.11.1
- https://medium.com/@sid0krypt/vue-js-reflected-xss-fae04c9872d2
