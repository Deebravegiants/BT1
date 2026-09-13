# [H] Parsing issue in matrix-org/node-irc leading to room takeovers

## Summary
Severity: High
Advisory: GHSA-xvqg-mv25-rwvw
CVE: CVE-2022-39203
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-15
Source: https://github.com/advisories/GHSA-xvqg-mv25-rwvw
Type: github-advisory

## Affected
- npm: `matrix-appservice-irc` — affected >=0 <0.35.0

## Details
### Impact

Attackers can specify a specific string of characters, which would confuse the bridge into combining an attacker-owned channel and an existing channel, allowing them to grant themselves permissions in the channel.

### Patched

The vulnerability has been patched in matrix-appservice-irc 0.35.0.

### Workarounds

Disable dynamic channel joining via `dynamicChannels.enabled` to prevent users from joining new channels, which prevents any new channels being bridged outside of what is already bridged, and what is specified in the config.

### References

- https://matrix.org/blog/2022/09/13/security-release-of-matrix-appservice-irc-0-35-0-high-severity

### Credits

Discovered and reported by [Val Lorentz](https://valentin-lorentz.fr/).

### For more information

If you have any questions or comments about this advisory email us at [security@matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/matrix-appservice-irc/security/advisories/GHSA-xvqg-mv25-rwvw
- https://nvd.nist.gov/vuln/detail/CVE-2022-39203
- https://github.com/matrix-org/matrix-appservice-irc
- https://matrix.org/blog/2022/09/13/security-release-of-matrix-appservice-irc-0-35-0-high-severity
