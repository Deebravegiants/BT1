# [C] Pterodactyl Panel Allows Cross-Node Server Configuration Disclosure via Remote API Missing Authorization

## Summary
Severity: Critical
Advisory: GHSA-g7vw-f8p5-c728
CVE: CVE-2026-26016
CWE: CWE-283, CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:L/SA:L (CVSS_V4)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-g7vw-f8p5-c728
Type: github-advisory

## Affected
- Packagist: `pterodactyl/panel` — affected >=0 <1.12.1

## Details
### Summary

A missing authorization check in multiple controllers allows any user with access to a node secret token to fetch information about any server on a Pterodactyl instance, even if that server is associated with a different node. This issue stems from missing logic to verify that the node requesting server data is the same node that the server is associated with.

Any authenticated Wings node can retrieve server installation scripts (potentially containing secret values) and manipulate the installation status of servers belonging to other nodes. Wings nodes may also manipulate the transfer status of servers belonging to other nodes.

_This vulnerability requires a user to acquire a secret access token for a node. We rated this issue based on potential worst outcome. Unless a user gains access to a Wings secret access token they would not be able to access any of these vulnerable endpoints, as every endpoint requires a valid node access token._

### Details
1. The Remote API endpoint `GET /api/remote/servers/{uuid}` fetches a server by UUID and returns its complete configuration without verifying that the requesting node owns the server.
2. Both failure() and success() methods in `ServerTransferController` fetch servers by UUID without verifying node ownership.
3. Missing authorization checks in `ServerInstallController` allow any authenticated Wings node to retrieve egg installation scripts (containing deployment secrets) and manipulate the installation status of servers belonging to other nodes.

### Impact
A single compromised Wings node daemon token (stored in plaintext at `/etc/pterodactyl/config.yml`) grants access to sensitive configuration data of every server on the panel, rather than only to servers that the node has access to. An attacker can use this information to move laterally through the system, send excessive notifications, destroy server data on other nodes, and otherwise exfiltrate secrets that they should not have access to with only a node token.

Additionally, triggering a false transfer success causes the panel to delete the server from the source node, resulting in permanent data loss.

## References
- https://github.com/pterodactyl/panel/security/advisories/GHSA-g7vw-f8p5-c728
- https://nvd.nist.gov/vuln/detail/CVE-2026-26016
- https://github.com/pterodactyl/panel
- https://github.com/pterodactyl/panel/releases/tag/v1.12.1
