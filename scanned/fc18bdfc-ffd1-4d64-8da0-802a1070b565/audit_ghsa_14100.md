# [H] Ghost vulnerable to information disclosure of private API fields

## Summary
Severity: High
Advisory: GHSA-r97q-ghch-82j9
CVE: CVE-2023-31133
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-03
Source: https://github.com/advisories/GHSA-r97q-ghch-82j9
Type: github-advisory

## Affected
- npm: `ghost` — affected >=0 <5.46.1

## Details
### Impact

Due to a lack of validation when filtering on the public API endpoints, it is possible to reveal private fields via a brute force attack.

Ghost(Pro) has already been patched. We can find no evidence that the issue was exploited on Ghost(Pro) prior to the patch being added.

Self-hosters are impacted if running Ghost a version below v5.46.1. Immediate action should be taken to secure your site - see patches and workarounds below.

### Patches

v5.46.1 contains a fix for this issue.

### Workarounds

Add a block for requests to `/ghost/api/content/*` where the `filter` query parameter contains `password` or `email`.

### For more information

If you have any questions or comments about this advisory:

* Email us at [security@ghost.org](mailto:security@ghost.org)

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-r97q-ghch-82j9
- https://nvd.nist.gov/vuln/detail/CVE-2023-31133
- https://github.com/TryGhost/Ghost/commit/b3caf16005289cc9909488391b4a26f3f4a66a90
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v5.46.1
