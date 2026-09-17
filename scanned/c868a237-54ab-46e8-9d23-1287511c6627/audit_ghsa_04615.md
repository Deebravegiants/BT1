# [M] Outerbase Studio: Stored XSS in Text Widget Leads to Authentication Token Exposure

## Summary
Severity: Medium
Advisory: GHSA-wwf9-7jrc-rv4q
CVE: CVE-2026-55650
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-wwf9-7jrc-rv4q
Type: github-advisory

## Affected
- npm: `@outerbase/studio` — affected >=0

## Details
## Summary

A Stored Cross-Site Scripting (XSS) issue previously existed in the Text Widget in Board of Outerbase Studio where unsanitized HTML could be rendered using `dangerouslySetInnerHTML`

### Steps to Reproduce

1. Create a new dashboard.
2. Add a **Text widget**.
3. Insert the following payload:

```html
<img src=x onerror="alert('XSS Executed\nToken: ' + localStorage.getItem('ob-token'))">
```

### Architectural Context

Outerbase Cloud and its backend services were discontinued in 2025.

The current version of Outerbase Studio operates purely as a client-side application, with dashboard data stored locally in the browser.

### Impact

In the current architecture, the impact is limited to local self-XSS within a user's browser session.
The previously described scenarios involving:

- authentication token theft
- account takeover
- database access

are no longer applicable since there are no active backend services or authentication tokens.

### Remediation

The unsafe HTML rendering in the Text Widget has been removed in commit https://github.com/outerbase/studio/commit/b06fb85e5967440278d5a815721b360920566ab9 by eliminating the use of dangerouslySetInnerHTML.

## References
- https://github.com/outerbase/studio/security/advisories/GHSA-wwf9-7jrc-rv4q
- https://github.com/outerbase/studio/commit/b06fb85e5967440278d5a815721b360920566ab9
- https://github.com/outerbase/studio
