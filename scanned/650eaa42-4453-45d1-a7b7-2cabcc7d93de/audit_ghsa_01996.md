# [H] Remote Command Execution in reg-keygen-git-hash-plugin

## Summary
Severity: High
Advisory: GHSA-49q3-8867-5wmp
CVE: CVE-2021-32673
CWE: CWE-78, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-49q3-8867-5wmp
Type: github-advisory

## Affected
- npm: `reg-keygen-git-hash-plugin` — affected >=0 <0.10.16

## Details
### Impact

`reg-keygen-git-hash-plugin` through 0.10.15 allow remote attackers to execute of arbitrary commands.

### Patches

Upgrade to version 0.10.16 or later.

### For more information

If you have any questions or comments about this advisory:
- Open an issue in [reg-viz/reg-suit](https://github.com/reg-viz/reg-suit)

## References
- https://github.com/reg-viz/reg-suit/security/advisories/GHSA-49q3-8867-5wmp
- https://nvd.nist.gov/vuln/detail/CVE-2021-32673
- https://github.com/reg-viz/reg-suit/commit/f84ad9c7a22144d6c147dc175c52756c0f444d87
- https://github.com/reg-viz/reg-suit/releases/tag/v0.10.16
- https://www.npmjs.com/package/reg-keygen-git-hash-plugin
