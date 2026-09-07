# [M] Gogs has DOM-based XSS via Milestone Name on New Issue Page

## Summary
Severity: Medium
Advisory: GHSA-vcm5-gvmp-78mp
CVE: CVE-2026-52807
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-vcm5-gvmp-78mp
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
### Summary
The fix for GHSA-vgjm-2cpf-4g7c (DOM-based XSS via milestone selection) was only applied to `templates/repo/issue/view_content.tmpl` but not to `templates/repo/issue/new_form.tmpl`. An attacker can store an HTML/JavaScript payload in a milestone name, and when any user opens the New Issue page and interacts with the milestone dropdown, the payload executes in their browser via Semantic UI's `preserveHTML` behavior.

### Details
GHSA-vgjm-2cpf-4g7c was patched by adding `| Sanitize` (bluemonday HTML tag stripping) to milestone name rendering in `view_content.tmpl`. However, the same milestone dropdown exists in `new_form.tmpl` and was **not** patched.

In `new_form.tmpl`, milestone names are rendered with Go's default auto-escaping (`{{.Name}}`), which converts `<` to `&lt;` etc. This prevents direct HTML injection. However, when the browser renders the DOM, the text content of the element contains the **decoded** original payload (e.g., `<img src=x onerror=alert(1)>`).

Semantic UI 2.4.2's dropdown component has `preserveHTML: true` as the default setting. When a user selects a dropdown item, the internal `set.text()` method calls jQuery's `.html()` with the item's text content. This re-parses the decoded text as HTML, creating the injected element and triggering the JavaScript event handler.

### PoC
[poc.zip](https://github.com/user-attachments/files/26508268/poc.zip)
Please extract the uploaded compressed file before proceeding

1. docker compose up --build

<img width="1325" height="315" alt="스크린샷 2026-04-06 오후 9 34 05" src="https://github.com/user-attachments/assets/87895cce-5b8e-4320-829a-87a5890cc0d9" />

### Impact
- Stored DOM XSS: Any user with write access to a repository can create a malicious milestone. Any other user who visits the New Issue page and interacts with the milestone dropdown will have arbitrary JavaScript executed in their browser session.
- Session hijacking: The attacker can steal session cookies, perform actions as the victim, or escalate privileges.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-vcm5-gvmp-78mp
- https://nvd.nist.gov/vuln/detail/CVE-2026-52807
- https://github.com/gogs/gogs/pull/8325
- https://github.com/gogs/gogs/commit/573eacdc658641487f8ad883da96b29ec8e2852d
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
