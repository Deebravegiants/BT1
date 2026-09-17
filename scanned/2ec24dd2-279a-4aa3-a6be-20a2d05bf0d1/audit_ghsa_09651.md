# [M] skilleton has improper input handling in repository/path processing

## Summary
Severity: Medium
Advisory: GHSA-5g3j-89fr-r2vp
CWE: CWE-1333, CWE-400, CWE-78, CWE-88
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-5g3j-89fr-r2vp
Type: github-advisory

## Affected
- npm: `skilleton` — affected >=0 <0.3.1

## Details
## Summary

`skilleton` versions prior to `0.3.1` include security-related weaknesses in repository normalization and path handling logic.  
Version `0.3.1` contains fixes and additional test coverage for these issues.

## Affected Versions

`<0.3.1`

## Patched Versions

`>=0.3.1`

## Impact

In affected versions, crafted input could trigger unsafe or inefficient behavior in repository/path processing code paths.  
`0.3.1` mitigates this by:
- replacing vulnerable parsing behavior with deterministic logic,
- validating subpaths earlier before allocating git worktree resources,
- adding stricter and broader regression tests around these flows.

## Severity

Low to Moderate (project-maintainer assessed)

## Mitigation

Upgrade to `0.3.1` or later.

## Workarounds

No complete workaround is recommended other than upgrading.

## References

- Branch: [`fix/security-code-scanning-alerts`](https://github.com/Fcmam5/skilleton/pull/9)
- Commits:
  - [fix(security): harden git arg handling and path validation](https://github.com/Fcmam5/skilleton/pull/9/changes/42bc280ad675bfaa7b1bbc192330fb582bb28172)
  - [fix(security): use while loop in normalizeRepoUrl instead of regex](https://github.com/Fcmam5/skilleton/pull/9/changes/6613160803ec8655efee9a270eeaa767ad22da8b)
- Security Policy: [SECURITY.md](https://github.com/Fcmam5/skilleton/blob/master/SECURITY.md)

## Credits

Detected through automated code scanning and remediated by project maintainers.

## References
- https://github.com/Fcmam5/skilleton/security/advisories/GHSA-5g3j-89fr-r2vp
- https://github.com/Fcmam5/skilleton/pull/9/changes/42bc280ad675bfaa7b1bbc192330fb582bb28172
- https://github.com/Fcmam5/skilleton/pull/9/changes/6613160803ec8655efee9a270eeaa767ad22da8b
- https://github.com/Fcmam5/skilleton
