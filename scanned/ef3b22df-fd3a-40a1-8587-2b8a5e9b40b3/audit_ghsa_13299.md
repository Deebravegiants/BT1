# [H] twitch-tui's connection is not encrypted

## Summary
Severity: High
Advisory: GHSA-779w-xvpm-78jx
CVE: CVE-2023-38688
CWE: CWE-311
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-31
Source: https://github.com/advisories/GHSA-779w-xvpm-78jx
Type: github-advisory

## Affected
- crates.io: `twitch-tui` — affected >=0 <2.4.1

## Details
### Summary
The connection is not using TLS for communication

### Details
In the configuration of the irc connection, [you are disabling tls](https://github.com/Xithrius/twitch-tui/blob/340afc3c8c07a83289fe6ef614aa7563c8b70756/src/twitch/connection.rs#L23) which makes all communication to twitch irc servers unencrypted.

### PoC
You can verify by using tcpdump/wireshark that traffic is unencrypted.

### Impact
Communication can be sniffed, even auth tokens.

## References
- https://github.com/Xithrius/twitch-tui/security/advisories/GHSA-779w-xvpm-78jx
- https://nvd.nist.gov/vuln/detail/CVE-2023-38688
- https://github.com/Xithrius/twitch-tui/commit/74d13ddca35f8f0816f4933c229da1fd95c0350a
- https://github.com/Xithrius/twitch-tui
- https://github.com/Xithrius/twitch-tui/blob/340afc3c8c07a83289fe6ef614aa7563c8b70756/src/twitch/connection.rs#L23
