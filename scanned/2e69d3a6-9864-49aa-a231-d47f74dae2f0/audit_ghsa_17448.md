# [M] CNA Plugins Portmap nftables backend can intercept non-local traffic

## Summary
Severity: Medium
Advisory: GHSA-jv3w-x3r3-g6rm
CVE: CVE-2025-67499
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2025-12-09
Source: https://github.com/advisories/GHSA-jv3w-x3r3-g6rm
Type: github-advisory

## Affected
- Go: `github.com/containernetworking/plugins` — affected >=1.6.0 <1.9.0

## Details
### Background

The CNI `portmap` plugin allows containers to emulate opening a host port, forwarding that traffic to the container. For example, if a host has the IP 198.51.100.42, a container may request that all packets to `198.51.100.42:53` be forwarded to the container's network.

### Vulnerability

When the `portmap` plugin is configured with the `nftables` backend, it inadvertently forwards all traffic with the same destination port as the host port, **ignoring the destination IP**. This includes traffic not intended for the node itself, i.e. traffic to containers hosted on the node.

In the given example above, traffic destined to port 53 but for a _separate container_ would still be captured and forwarded, even though it was not destined for the host.

### Impact

Containers (i.e. kubernetes pods) that request HostPort forwarding can intercept all traffic destined for that port. This requires that the `portmap` plugin be explicitly configured to use the `nftables` backend. (The `iptables` backend is the default.)

### Patches
This is fixed as of CNI plugins v1.9.0

### Workarounds
Configure the `portmap` plugin to use the `iptables` backend. It does not have this vulnerability.

## References
- https://github.com/containernetworking/plugins/security/advisories/GHSA-jv3w-x3r3-g6rm
- https://nvd.nist.gov/vuln/detail/CVE-2025-67499
- https://github.com/containernetworking/plugins/pull/1210
- https://github.com/containernetworking/plugins/commit/9b3772e1a7abf93cbb7c6526a28bc0d27b830e02
- https://github.com/containernetworking/plugins
- https://github.com/containernetworking/plugins/releases/tag/v1.9.0
- https://pkg.go.dev/vuln/GO-2026-4222
