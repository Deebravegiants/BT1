# [M] OpenClaw's browser act interactions could bypass private-network navigation checks

## Summary
Severity: Medium
Advisory: GHSA-2hfg-4fh4-qp7f
CVE: CVE-2026-53812
CWE: CWE-284, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-2hfg-4fh4-qp7f
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.18

## Details
### Summary

OpenClaw's browser control SSRF checks blocked direct navigation to private or loopback URLs, but some Playwright `act` interactions could trigger navigation after the initial check. A later browser evaluation could then read from the page reached by that action-triggered navigation.

This issue is specific to browser control actions and private-network navigation policy. Browser evaluation remains an intentional trusted-operator feature when it is used on pages that policy allowed the browser to visit.

### Affected configurations

This affects deployments where browser control is enabled and an authenticated browser-control caller can interact with an attacker-controlled page that redirects or navigates the tab to a private-network target through a UI action.

### Impact

If the browser reached a private page through an unchecked action-triggered navigation, a caller with browser evaluation capability could read page content that direct navigation policy would have blocked.

The issue does not grant access to OpenClaw without authentication. It bypasses the private-network navigation guard for a specific browser action path.

### Patched Versions

The first stable patched version is `2026.5.18`.

### Mitigations

Upgrade to `openclaw@2026.5.18` or later. Before upgrading, restrict browser-control access to trusted operators and avoid using browser control on untrusted pages in environments with sensitive private web services.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2hfg-4fh4-qp7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-53812
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-private-network-navigation-bypass-via-browser-act-interactions
