# [C] NodeBB vulnerable to account takeover via prototype vulnerability

## Summary
Severity: Critical
Advisory: GHSA-rf3g-v8p5-p675
CVE: CVE-2022-46164
CWE: CWE-665
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2022-12-05
Source: https://github.com/advisories/GHSA-rf3g-v8p5-p675
Type: github-advisory

## Affected
- npm: `nodebb` — affected >=0 <2.6.1

## Details
### Impact
Due to a plain object with a prototype being used in socket.io message handling a specially crafted payload can be used to impersonate other users and takeover accounts.

### Patches
Patched in 2.6.1

### Workarounds
Site maintainers can cherry-pick https://github.com/NodeBB/NodeBB/commit/48d143921753914da45926cca6370a92ed0c46b8 into their codebase to patch the exploit.

### For more information
If you have any questions or comments about this advisory:

Discuss it on [our community forum](https://github.com/NodeBB/NodeBB/security/advisories/community.nodebb.org/)
Email us at [support@nodebb.org](mailto:support@nodebb.org)

## References
- https://github.com/NodeBB/NodeBB/security/advisories/GHSA-rf3g-v8p5-p675
- https://nvd.nist.gov/vuln/detail/CVE-2022-46164
- https://github.com/NodeBB/NodeBB/commit/48d143921753914da45926cca6370a92ed0c46b8
- https://github.com/NodeBB/NodeBB
- https://github.com/NodeBB/NodeBB/releases/tag/v2.6.1
