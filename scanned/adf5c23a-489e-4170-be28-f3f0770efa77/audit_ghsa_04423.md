# [M] NocoDB: Reflected Cross-Site Scripting via Password Reset Token

## Summary
Severity: Medium
Advisory: GHSA-6xcx-7qmg-vjfq
CVE: CVE-2026-47376
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-6xcx-7qmg-vjfq
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <2026.04.1

## Details
### Summary

The password-reset page rendered the URL token directly into a JavaScript string literal in a server-rendered EJS template. EJS `<%= %>` HTML-entity-encodes a fixed set of characters but does not escape single quotes or backslashes, so a crafted token could break out of the JS string context and execute attacker-controlled script in the NocoDB origin. Triggering required only that a victim follow a malicious password-reset link.

### Details

The vulnerable template embedded the token as:

```ejs
token: '<%= token %>',
```

A token containing `';alert(document.cookie);//` closes the single-quoted string and runs arbitrary JavaScript. The fix moves the token into an HTML attribute (`data-token="…"`) and reads it from `dataset.token` at runtime, so EJS's HTML-entity escaping is sufficient.

### Impact

- Reflected XSS in the NocoDB origin via a phished password-reset URL.
- No authentication required to trigger; affects any user who clicks the crafted link.
- Same-origin script can read auth state and act on the victim's behalf.

### Credit

This issue was reported by [@fg0x0](https://github.com/fg0x0).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-6xcx-7qmg-vjfq
- https://nvd.nist.gov/vuln/detail/CVE-2026-47376
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/2026.04.1
