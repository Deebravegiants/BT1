# [H] Vikunja Vulnerable to XSS Via Task Preview

## Summary
Severity: High
Advisory: GHSA-m4g2-2q66-vc9v
CVE: CVE-2026-25935
CWE: CWE-79, CWE-80
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-11
Source: https://github.com/advisories/GHSA-m4g2-2q66-vc9v
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0

## Details
### Summary
The task preview component creates a unparented div. The div's `innerHtml` is set to the unescaped description of the task

### Details
In the `TaskGlanceTooltip.vue` it temporarily creates a div and sets the `innerHtml` to the description [here](https://github.com/go-vikunja/vikunja/blob/cdca79032526966cb248b72bddcf2a0f888c8a8f/frontend/src/components/tasks/partials/TaskGlanceTooltip.vue#L118). Since there is no escaping on either the server or client side, a malicious user can share a project, create a malicious task, and cause an XSS on hover.

### PoC
1. Create a project
2. Create a task with any description
3. Use the api to update the task with a description containing unescaped HTML (ex: `<img src=x onerror="alert(localStorage.getItem('token'))">`
4. Share the project with any permission level
5. Send malicious project to user and ask them to view task

### Impact
Any user on an instance can cause an XSS on another

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-m4g2-2q66-vc9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-25935
- https://github.com/go-vikunja/vikunja/commit/dd0b82f00a8c9ded1c19a1e643a197c514be6d37
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v1.1.0
- https://vikunja.io/changelog/vikunja-v1.1.0-was-released
