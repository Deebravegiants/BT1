# [H] TrustTunnel has SSRF and private network restriction bypass via numeric address destinations

## Summary
Severity: High
Advisory: CVE-2026-24902
Aliases: GHSA-hgr9-frvw-5r76
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-01-29
Source: https://osv.dev/vulnerability/CVE-2026-24902
Type: osv

## Details
TrustTunnel is an open-source VPN protocol with a server-side request forgery and and private network restriction bypass in versions prior to 0.9.114. In `tcp_forwarder.rs`, SSRF protection for `allow_private_network_connections = false` was only applied in the `TcpDestination::HostName(peer)` path. The `TcpDestination::Address(peer) => peer` path proceeded to `TcpStream::connect()` without equivalent checks (for example `is_global_ip`, `is_loopback`), allowing loopback/private targets to be reached by supplying a numeric IP. The vulnerability is fixed in version 0.9.114.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24902.json
- https://github.com/TrustTunnel/TrustTunnel/security/advisories/GHSA-hgr9-frvw-5r76
- https://nvd.nist.gov/vuln/detail/CVE-2026-24902
- https://github.com/TrustTunnel/TrustTunnel/commit/734bb5cf103b72390a95c853cbf91e699cc01bc0
