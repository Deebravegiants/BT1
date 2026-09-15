# [H] Synapse allows a a malformed invite to break the invitee's `/sync`

## Summary
Severity: High
Advisory: GHSA-f3r3-h2mq-hx2h
CVE: CVE-2024-52815
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-12-03
Source: https://github.com/advisories/GHSA-f3r3-h2mq-hx2h
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.120.1

## Details
### Impact

Synapse versions before 1.120.1 fail to properly validate invites received over federation. This vulnerability allows a malicious server to send a specially crafted invite that disrupts the invited user's `/sync` functionality.

### Patches

Synapse 1.120.1 rejects such invalid invites received over federation and restores the ability to sync for affected users.

### Workarounds

Server administrators can disable federation from untrusted servers.

### For more information

If you have any questions or comments about this advisory, please email us at [security at element.io](mailto:security@element.io).

## References
- https://github.com/element-hq/synapse/security/advisories/GHSA-f3r3-h2mq-hx2h
- https://nvd.nist.gov/vuln/detail/CVE-2024-52815
- https://github.com/element-hq/synapse
