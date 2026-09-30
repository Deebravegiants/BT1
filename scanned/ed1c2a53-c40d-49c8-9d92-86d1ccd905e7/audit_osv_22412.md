# [H] Improper handling of multiline messages in matrix-appservice-irc

## Summary
Severity: High
Advisory: CVE-2022-29166
Aliases: GHSA-37hr-348p-rmf4
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-05-05
Source: https://osv.dev/vulnerability/CVE-2022-29166
Type: osv

## Details
matrix-appservice-irc is a Node.js IRC bridge for Matrix. The vulnerability in node-irc allows an attacker to manipulate a Matrix user into executing IRC commands by having them reply to a maliciously crafted message. The vulnerability has been patched in matrix-appservice-irc 0.33.2. Refrain from replying to messages from untrusted participants in IRC-bridged Matrix rooms. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29166.json
- https://github.com/matrix-org/matrix-appservice-irc/security/advisories/GHSA-37hr-348p-rmf4
- https://nvd.nist.gov/vuln/detail/CVE-2022-29166
- https://matrix.org/blog/2022/05/04/0-34-0-security-release-for-matrix-appservice-irc-high-severity
