# [M] Coder vulnerable to stored HTML injection via workspace agent logs in AgentLogLine component

## Summary
Severity: Medium
Advisory: GHSA-7qw2-f75v-62f7
CVE: CVE-2026-55437
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-7qw2-f75v-62f7
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.7
- Go: `github.com/coder/coder/v2` — affected >=0 <2.29.17

## Details
### Summary

The `AgentLogLine` dashboard component instantiated `ansi-to-html` without `escapeXML: true` and inserted the result via `dangerouslySetInnerHTML` so HTML embedded in workspace agent log lines was rendered as live markup. Server-side sanitization did not neutralize HTML metacharacters.

> **Note:** Exploitation requires a victim to view attacker-controlled agent logs in the dashboard.

### Impact

A user who could run a workspace could emit arbitrary HTML into agent logs; when another user, including an administrator, viewed the workspace page, it rendered in their session. Content Security Policy blocked inline scripts but an attacker could still inject a `meta refresh` redirect, `style` rules for UI redressing or CSS-based exfiltration or external `img` beacons. This required workspace-owner access and a victim viewing the page.

### Patches

The fix enables `escapeXML: true` so HTML metacharacters are escaped before DOM insertion.

The fix was backported to all supported release lines:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |
| 2.32 | [v2.32.7](https://github.com/coder/coder/releases/tag/v2.32.7) |
| 2.29 (ESR) | [v2.29.17](https://github.com/coder/coder/releases/tag/v2.29.17) |

### Workarounds

None.

### Resources

- Fix: #25808

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22449) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-7qw2-f75v-62f7
- https://github.com/coder/coder/pull/25808
- https://github.com/coder/coder
