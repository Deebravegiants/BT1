# [M] Matrix IRC Bridge truncated content of messages can be leaked

## Summary
Severity: Medium
Advisory: GHSA-wm4w-7h2q-3pf7
CVE: CVE-2024-32000
CWE: CWE-280
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-04-11
Source: https://github.com/advisories/GHSA-wm4w-7h2q-3pf7
Type: github-advisory

## Affected
- npm: `matrix-appservice-irc` — affected >=0 <2.0.0

## Details
### Impact

The matrix-appservice-irc before version 2.0.0 can be exploited to leak the truncated body of a message if a malicious user sends a Matrix reply to an event ID they don't have access to. As a precondition to the attack, the malicious user needs to know the event ID of the message they want to leak, as well as to be joined to both the Matrix room and the IRC channel it is bridged to.

The message reply containing the leaked message content is visible to IRC channel members when this happens.

### Patches

matrix-appservice-irc 2.0.0 checks whether the user has permission to view an event before constructing a reply. Administrators should upgrade to this version.

### Workarounds

It's possible to limit the amount of information leaked by setting a reply template that doesn't contain the original message. See [these lines](https://github.com/matrix-org/matrix-appservice-irc/blob/d5d67d1d3ea3f0f6962a0af2cc57b56af3ad2129/config.sample.yaml#L601-L604) in the configuration file.

### References
https://github.com/matrix-org/matrix-appservice-irc/pull/1799

### For more information

If you have any questions or comments about this advisory, please email us at [security at matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/matrix-appservice-irc/security/advisories/GHSA-wm4w-7h2q-3pf7
- https://nvd.nist.gov/vuln/detail/CVE-2024-32000
- https://github.com/matrix-org/matrix-appservice-irc/pull/1799
- https://github.com/matrix-org/matrix-appservice-irc/commit/4af7d3009f10b1f2fb810784c1e491d9d3bee82b
- https://github.com/matrix-org/matrix-appservice-irc
- https://github.com/matrix-org/matrix-appservice-irc/blob/d5d67d1d3ea3f0f6962a0af2cc57b56af3ad2129/config.sample.yaml#L601-L604
