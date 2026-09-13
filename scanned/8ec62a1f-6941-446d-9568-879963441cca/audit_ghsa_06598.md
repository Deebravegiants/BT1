# [M] Pion STUN vulnerable to remote denial of service via panic while parsing a malformed XOR-MAPPED-ADDRESS attribute

## Summary
Severity: Medium
Advisory: GHSA-34rh-wp3j-6cxc
CVE: CVE-2026-54909
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-34rh-wp3j-6cxc
Type: github-advisory

## Affected
- Go: `github.com/pion/stun/v3` — affected >=0 <3.1.5
- Go: `github.com/pion/stun/v2` — affected >=0
- Go: `github.com/pion/stun` — affected >=0

## Details
### Impact
Remote denial of service via panic while parsing a malformed XOR-MAPPED-ADDRESS attribute

### Patches
Upgrade to v3.1.5 or later. This version includes this patch https://github.com/pion/stun/pull/278 which fixes the issue.

### Workarounds
No work around; please upgrade to v3.1.5 or a newer version.

## References
- https://github.com/pion/stun/security/advisories/GHSA-34rh-wp3j-6cxc
- https://github.com/pion/stun/pull/278
- https://github.com/pion/stun/commit/fa9f074a33a8059c76c960b1fbee39f308002423
- https://github.com/pion/stun
- https://github.com/pion/stun/releases/tag/v3.1.3
