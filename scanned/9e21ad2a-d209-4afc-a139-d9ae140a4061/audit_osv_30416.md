# [M] matrix-appservice-irc allows IRC Command injection in provisioning API

## Summary
Severity: Medium
Advisory: CVE-2024-52505
Aliases: GHSA-c3hj-hg7p-rrq5
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-11-14
Source: https://osv.dev/vulnerability/CVE-2024-52505
Type: osv

## Details
matrix-appservice-irc is a Node.js IRC bridge for the Matrix messaging protocol. The provisioning API of the matrix-appservice-irc bridge up to version 3.0.2 contains a vulnerability which can lead to arbitrary IRC command execution as the bridge IRC bot. The vulnerability has been patched in matrix-appservice-irc version 3.0.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52505.json
- https://github.com/matrix-org/matrix-appservice-irc/security/advisories/GHSA-c3hj-hg7p-rrq5
- https://nvd.nist.gov/vuln/detail/CVE-2024-52505
- https://github.com/matrix-org/matrix-appservice-irc/commit/4a024eae1a992b1ea67e71a998e0b833b54221e2
