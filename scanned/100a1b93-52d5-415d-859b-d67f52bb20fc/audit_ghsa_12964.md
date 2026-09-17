# [M] matrix-appservice-irc IRC command injection via admin commands containing newlines 

## Summary
Severity: Medium
Advisory: GHSA-3pmj-jqqp-2mj3
CVE: CVE-2023-38690
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2023-08-04
Source: https://github.com/advisories/GHSA-3pmj-jqqp-2mj3
Type: github-advisory

## Affected
- npm: `matrix-appservice-irc` — affected >=0 <1.0.1

## Details
### Impact

It is possible to craft a command with newlines which would not be properly parsed. This would mean you could pass a string of commands as a channel name, which would then be run by the IRC bridge bot. 

### Patches

Versions 1.0.1 and above are patched.

### Workarounds

There are no robust workarounds to the bug. You can disable dynamic channels in the config to disable the most common execution method but others may exist. It is highly recommended to upgrade the bridge.

### Credits

Discovered and reported by [Val Lorentz](https://valentin-lorentz.fr/).

### For more information

If you have any questions or comments about this advisory email us at [security@matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/matrix-appservice-irc/security/advisories/GHSA-3pmj-jqqp-2mj3
- https://nvd.nist.gov/vuln/detail/CVE-2023-38690
- https://github.com/matrix-org/matrix-appservice-irc/commit/0afb064635d37e039067b5b3d6423448b93026d3
- https://github.com/matrix-org/matrix-appservice-irc
- https://github.com/matrix-org/matrix-appservice-irc/releases/tag/1.0.1
