# [H] Daytona: Public sandbox previews remain accessible for up to one hour after being made private

## Summary
Severity: High
Advisory: GHSA-ww63-pv5x-vfc8
CVE: CVE-2026-54321
CWE: CWE-613, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-ww63-pv5x-vfc8
Type: github-advisory

## Affected
- Go: `github.com/daytonaio/daytona` — affected >=0.101.0 <0.184.0

## Details
### Summary
Sandbox previews that were switched from public to private could remain reachable without authentication for a short period after the change, due to a cached visibility state that was not invalidated when the sandbox's visibility changed.

### Impact
When a sandbox owner changed a preview from public to private, the preview proxy could continue serving unauthenticated requests to that sandbox's ordinary preview ports for a bounded period before the change took effect. Only sandboxes that had been made public and were later set back to private were affected, and only until the proxy's cached visibility state was refreshed. Terminal, toolbox, and recording-dashboard ports were never affected, as those always require authentication. The issue did not involve cross-tenant access, privilege escalation, or remote code execution.

### Patches
Fixed in v0.184.0. Sandbox visibility changes now invalidate the proxy's cached preview state immediately, so revoking a public preview takes effect on the next request.

### Workarounds
Upgrade to v0.184.0 or later. There is no configuration workaround for earlier versions.

### Credit
Reported through Daytona's Vulnerability Disclosure Program by **mrknightnidu(nidalkhan)**.
**Linkedin**: https://www.linkedin.com/in/mrknight-nidu-031340328/

## References
- https://github.com/daytonaio/daytona/security/advisories/GHSA-ww63-pv5x-vfc8
- https://nvd.nist.gov/vuln/detail/CVE-2026-54321
- https://github.com/daytonaio/daytona
