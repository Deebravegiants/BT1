# [M] matrix-appservice-irc vulnerable to IRC mode parameter confusion

## Summary
Severity: Medium
Advisory: GHSA-cq7q-5c67-w39w
CVE: CVE-2022-39202
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-09-15
Source: https://github.com/advisories/GHSA-cq7q-5c67-w39w
Type: github-advisory

## Affected
- npm: `matrix-appservice-irc` — affected >=0 <0.35.0

## Details
### Impact

IRC allows you to specify multiple modes in a single mode command. Due to a bug in the underlying matrix-org/node-irc library, affected versions of matrix-appservice-irc perform parsing of such modes incorrectly, potentially resulting in the wrong user being given permissions.

Mode commands can only be executed by privileged users, so this can only be abused if an operator is tricked into running the command on behalf of an attacker.

### Patches

The vulnerability has been patched in matrix-appservice-irc 0.35.0.

### Workarounds

Refrain from entering mode commands suggested by untrusted users. Avoid using multiple modes in a single command.

### References

- https://matrix.org/blog/2022/09/13/security-release-of-matrix-appservice-irc-0-35-0-high-severity

### Credits

Discovered and reported by [Val Lorentz](https://valentin-lorentz.fr/).

### For more information

If you have any questions or comments about this advisory email us at [security@matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/matrix-appservice-irc/security/advisories/GHSA-cq7q-5c67-w39w
- https://nvd.nist.gov/vuln/detail/CVE-2022-39202
- https://github.com/matrix-org/matrix-appservice-irc/commit/5f87dbed87b4b6dc49b7965ff152ee8535719e67
- https://github.com/matrix-org/matrix-appservice-irc
- https://matrix.org/blog/2022/09/13/security-release-of-matrix-appservice-irc-0-35-0-high-severity
