# [M] Malicious Matrix homeserver can leak truncated message content of messages it shouldn't have access to

## Summary
Severity: Medium
Advisory: GHSA-w9mh-5x8j-9754
CVE: CVE-2024-39691
CWE: CWE-280, CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-07-05
Source: https://github.com/advisories/GHSA-w9mh-5x8j-9754
Type: github-advisory

## Affected
- npm: `matrix-appservice-irc` — affected >=0 <2.0.1

## Details
### Impact

The fix for GHSA-wm4w-7h2q-3pf7 / [CVE-2024-32000](https://www.cve.org/CVERecord?id=CVE-2024-32000) included in matrix-appservice-irc 2.0.0 relied on the Matrix homeserver-provided timestamp to determine whether a user has access to the event they're replying to when determining whether or not to include a truncated version of the original event in the IRC message. Since this value is controlled by external entities, a malicious Matrix homeserver joined to a room in which a matrix-appservice-irc bridge instance (before version 2.0.1) is present can fabricate the timestamp with the intent of tricking the bridge into leaking room messages the homeserver should not have access to.

### Patches

matrix-appservice-irc 2.0.1 [drops the reliance](https://github.com/matrix-org/matrix-appservice-irc/pull/1804) on `origin_server_ts` when determining whether or not an event should be visible to a user, instead tracking the event timestamps internally.

### Workarounds

It's possible to limit the amount of information leaked by setting a reply template that doesn't contain the original message. See [these lines](https://github.com/matrix-org/matrix-appservice-irc/blob/d5d67d1d3ea3f0f6962a0af2cc57b56af3ad2129/config.sample.yaml#L601-L604) in the configuration file.

### References

- Patch: https://github.com/matrix-org/matrix-appservice-irc/pull/1804

### For more information

If you have any questions or comments about this advisory, please email us at [security at matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/matrix-appservice-irc/security/advisories/GHSA-w9mh-5x8j-9754
- https://nvd.nist.gov/vuln/detail/CVE-2024-39691
- https://github.com/matrix-org/matrix-appservice-irc/pull/1804
- https://github.com/matrix-org/matrix-appservice-irc/commit/1835e047f269001054be4c68867797aa12372a0f
- https://github.com/matrix-org/matrix-appservice-irc
- https://github.com/matrix-org/matrix-appservice-irc/blob/d5d67d1d3ea3f0f6962a0af2cc57b56af3ad2129/config.sample.yaml#L601-L604
