# [H] Coturn: IPv4-mapped 127.0.0.1 bypasses default loopback peer protection

## Summary
Severity: High
Advisory: CVE-2026-53450
Aliases: GHSA-w4hf-cr3w-6h79
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-53450
Type: osv

## Details
Coturn is a free open source implementation of TURN and STUN Server. Prior to 4.13.0, coturn rejects loopback peers by default unless allow-loopback-peers is enabled, but the default loopback guard can be bypassed by using the IPv4-mapped IPv6 peer address ::ffff:127.0.0.1 in a TURN XOR-PEER-ADDRESS attribute. ioa_addr_is_loopback checks for the literal IPv6 loopback shape before IPv4-mapped IPv6 handling, so good_peer_addr does not apply the default loopback rejection and an authenticated TURN client can expose services bound only to localhost on the coturn host through TURN relay traffic. This issue is fixed in version 4.13.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53450.json
- https://github.com/coturn/coturn/security/advisories/GHSA-w4hf-cr3w-6h79
- https://nvd.nist.gov/vuln/detail/CVE-2026-53450
- https://github.com/coturn/coturn/commit/b057acbebe721c8f2f202ddad5e16289e295c754
