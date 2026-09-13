# [H] Soft Serve Affected by an Authentication Bypass

## Summary
Severity: High
Advisory: GHSA-pchf-49fh-w34r
CVE: CVE-2026-24058
CWE: CWE-289
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-pchf-49fh-w34r
Type: github-advisory

## Affected
- Go: `github.com/charmbracelet/soft-serve` — affected >=0 <0.11.3

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

This issue impacts every Soft Serve instance.

A critical authentication bypass allows an attacker to impersonate any user (including Admin) by "offering" the victim's public key during the SSH handshake before authenticating with their own valid key. This occurs because the user identity is stored in the session context during the "offer" phase and is not cleared if that specific authentication attempt fails.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Yes, please upgrade to version 0.11.3 as soon as possible.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

You need to upgrade

## References
- https://github.com/charmbracelet/soft-serve/security/advisories/GHSA-pchf-49fh-w34r
- https://nvd.nist.gov/vuln/detail/CVE-2026-24058
- https://github.com/charmbracelet/soft-serve/commit/8539f9ad39918b67d612a35785a2b4326efc8741
- https://github.com/charmbracelet/soft-serve
- https://github.com/charmbracelet/soft-serve/releases/tag/v0.11.3
