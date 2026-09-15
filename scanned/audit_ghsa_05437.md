# [H] Pterodactyl websocket endpoints have no visible rate limits or monitoring, allowing for DOS attacks

## Summary
Severity: High
Advisory: GHSA-8w7m-w749-rx98
CVE: CVE-2025-69199
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-8w7m-w749-rx98
Type: github-advisory

## Affected
- Go: `github.com/pterodactyl/wings` — affected >=0 <1.12.0

## Details
### Summary
Websockets within wings lack proper rate limiting and throttling. As a result a malicious user can open a large number of connections and then request data through these sockets, causing an excessive volume of data over the network and overloading the host system memory and cpu.

Additionally, there is not a limit applied to the total size of messages being sent or received, allowing a malicious user to open thousands of websocket connections and then send massive volumes of information over the socket, overloading the host network, and causing increased CPU and memory load within Wings.

## References
- https://github.com/pterodactyl/panel/security/advisories/GHSA-8w7m-w749-rx98
- https://nvd.nist.gov/vuln/detail/CVE-2025-69199
- https://github.com/pterodactyl/panel/commit/09caa0d4995bd924b53b9a9e9b4883ac27bd5607
- https://github.com/pterodactyl/panel
- https://github.com/pterodactyl/panel/releases/tag/v1.12.0
