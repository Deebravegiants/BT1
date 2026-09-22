# [M] Privilege escalation: all users can access Admin-level API keys

## Summary
Severity: Medium
Advisory: GHSA-j5c2-hm46-wp5c
CVE: CVE-2021-39192
CWE: CWE-200, CWE-269
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-07-22
Source: https://github.com/advisories/GHSA-j5c2-hm46-wp5c
Type: github-advisory

## Affected
- npm: `ghost` — affected >=4.0.0 <4.10.0

## Details
### Impact
An error in the implementation of the limits service in 4.0.0 allows all authenticated users (including contributors) to view admin-level API keys via the integrations API endpoint, leading to a privilege escalation vulnerability.

Ghost(Pro) has already been patched. Self-hosters are impacted if running Ghost a version between 4.0.0 and 4.9.4. Immediate action should be taken to secure your site - see patches & workarounds below.

It is highly recommended to regenerate all API keys after patching or applying the workaround below.

### Patches
Fixed in 4.10.0, all 4.x sites should upgrade as soon as possible.

### Workarounds
- Disable all non-Administrator accounts to prevent API access.

### For more information
If you have any questions or comments about this advisory:
* email us at security@ghost.org

---
Credits: Aden Yap Chuen Zhen, BAE Systems Applied Intelligence (Malaysia)

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-j5c2-hm46-wp5c
- https://nvd.nist.gov/vuln/detail/CVE-2021-39192
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v4.10.0
