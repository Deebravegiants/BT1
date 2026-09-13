# [H] CoreDNS: proxyproto plugin panics on PPv2 datagram with non-UDP transport — single 28-byte packet remote DoS

## Summary
Severity: High
Advisory: CVE-2026-62309
Aliases: GHSA-9rvv-m5g5-wc8r
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-62309
Type: osv

## Details
CoreDNS is a DNS server written in Go. Prior to 1.14.4, a single 28-byte UDP datagram can crash the CoreDNS process when the proxyproto plugin is enabled because plugin/pkg/proxyproto/proxyproto.go PacketConn.ReadFrom handles a PROXY v2 header with non-UDP transport such as family byte 0x11, reassigns addr from a nil readFrom result after parseProxyProtocol errors, and calls addr.String() in the warning log before ServeDNS recovery applies. This issue is fixed in version 1.14.4.

## References
- https://github.com/coredns/coredns/releases/tag/v1.14.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62309.json
- https://github.com/coredns/coredns/security/advisories/GHSA-9rvv-m5g5-wc8r
- https://nvd.nist.gov/vuln/detail/CVE-2026-62309
- https://github.com/coredns/coredns/commit/60a439dd4febfcd78e3779e952fe3fbf3c16bb1f
- https://github.com/coredns/coredns/pull/8154
