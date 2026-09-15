# [C] Termix: Remote Code Execution via Tunnel Disconnect pkill Command Injection

## Summary
Severity: Critical
Advisory: CVE-2026-53545
Aliases: GHSA-5p86-jgr7-4hwx
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-53545
Type: osv

## Details
Termix is a web-based server management platform with SSH terminal, tunneling, and file editing capabilities. Prior to 2.3.2, the DELETE /ssh/tunnel/disconnect/:tunnelName teardown path in src/backend/ssh/tunnel.ts interpolates endpointPort, sourcePort, endpointUsername, and endpointIP into single-quoted pkill -f patterns. An authenticated user who can edit a tunnel host field can include a single quote to terminate the pattern and append a shell command, which executes when the tunnel is disconnected. Successful exploitation runs arbitrary commands on the source SSH host with the privileges of the connected SSH account. This issue is fixed in version 2.3.2.

## References
- https://github.com/Termix-SSH/Termix/releases/tag/release-2.3.2-tag
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53545.json
- https://github.com/Termix-SSH/Termix/security/advisories/GHSA-5p86-jgr7-4hwx
- https://nvd.nist.gov/vuln/detail/CVE-2026-53545
- https://github.com/Termix-SSH/Termix/commit/52f4e51ae03b5b8d2608e1383e2ccf79d290132b
- https://github.com/Termix-SSH/Termix/pull/874
