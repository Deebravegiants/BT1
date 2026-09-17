# [H] Perry < 0.5.1159 Path Traversal via ArtifactReady WebSocket

## Summary
Severity: High
Advisory: CVE-2026-53777
Aliases: GHSA-x55v-q459-68ch
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-53777
Type: osv

## Details
Perry before 0.5.1159 contains a path traversal vulnerability that allows a malicious build server to write arbitrary content to any location writable by the running process by supplying unsanitized path components in the artifact_name field of ArtifactReady WebSocket messages. Attackers controlling the server URL can deliver traversal payloads through the artifact_name or download_path fields, causing the client to overwrite sensitive files or expose arbitrary local files to an attacker-accessible location.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53777.json
- https://github.com/PerryTS/perry/releases/tag/v0.5.1159
- https://github.com/PerryTS/perry/security/advisories/GHSA-x55v-q459-68ch
- https://nvd.nist.gov/vuln/detail/CVE-2026-53777
- https://www.vulncheck.com/advisories/perry-path-traversal-via-artifactready-websocket
- https://github.com/PerryTS/perry/pull/4989
- https://github.com/PerryTS/perry/commit/95e1043df8081f67038bffce847dd9ddb3dae046
- https://github.com/PerryTS/perry
