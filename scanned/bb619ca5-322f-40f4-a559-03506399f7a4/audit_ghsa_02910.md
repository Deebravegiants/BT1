# [M] NodeBB vulnerable to path traversal in translator module

## Summary
Severity: Medium
Advisory: GHSA-pfj7-2qfw-vwgm
CVE: CVE-2021-43788
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2021-11-30
Source: https://github.com/advisories/GHSA-pfj7-2qfw-vwgm
Type: github-advisory

## Affected
- npm: `nodebb` — affected >=1.0.4 <1.18.5

## Details
### Impact
Prior to v1.18.5, a path traversal vulnerability was present that allowed users to access JSON files outside of the expected `languages/` directory.

### Patches
The vulnerability has been patched as of v1.18.5.

### Workarounds
Cherry-pick commit hash `c8b2fc46dc698db687379106b3f01c71b80f495f` to receive this patch in lieu of a full upgrade.

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@nodebb.org](mailto:security@nodebb.org)

## References
- https://github.com/NodeBB/NodeBB/security/advisories/GHSA-pfj7-2qfw-vwgm
- https://nvd.nist.gov/vuln/detail/CVE-2021-43788
- https://github.com/NodeBB/NodeBB/commit/c8b2fc46dc698db687379106b3f01c71b80f495f
- https://blog.sonarsource.com/nodebb-remote-code-execution-with-one-shot
- https://github.com/NodeBB/NodeBB
- https://github.com/NodeBB/NodeBB/releases/tag/v1.18.5
