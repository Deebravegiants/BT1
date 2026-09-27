# [H] Improper handling of multiline messages in node-irc

## Summary
Severity: High
Advisory: GHSA-52rh-5rpj-c3w6
CWE: CWE-74, CWE-93
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-52rh-5rpj-c3w6
Type: github-advisory

## Affected
- npm: `matrix-org-irc` — affected >=0 <1.2.1

## Details
node-irc is a socket wrapper for the IRC protocol that extends Node.js' EventEmitter. The vulnerability allows an attacker to manipulate a Matrix user into executing IRC commands by having them reply to a maliciously crafted message. Incorrect handling of a CR character allowed for making part of the message be sent to the IRC server verbatim rather than as a message to the channel.
The vulnerability has been patched in node-irc version 1.2.1.

## References
- https://github.com/matrix-org/node-irc/security/advisories/GHSA-52rh-5rpj-c3w6
- https://nvd.nist.gov/vuln/detail/CVE-2022-29166
- https://github.com/matrix-org/node-irc/commit/2976c856df37660a9d664e94c857c796de2e34f7
- https://github.com/matrix-org/node-irc/commit/e3eb9c15f8240e9c92365f5ffc3944469229771b
- https://github.com/matrix-org/node-irc
- https://matrix.org/blog/2022/05/04/0-34-0-security-release-for-matrix-appservice-irc-high-severity
