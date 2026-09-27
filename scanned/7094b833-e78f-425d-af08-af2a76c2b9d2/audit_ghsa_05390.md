# [M] CoreDNS gRPC/HTTPS/HTTP3 servers lack resource limits, enabling DoS via unbounded connections and oversized messages

## Summary
Severity: Medium
Advisory: GHSA-527x-5wrf-22m2
CVE: CVE-2025-68151
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-527x-5wrf-22m2
Type: github-advisory

## Affected
- Go: `github.com/coredns/coredns` — affected >=0 <1.14.0

## Details
Multiple CoreDNS server implementations (gRPC, HTTPS, and HTTP/3) lack critical resource-limiting controls. An unauthenticated remote attacker can exhaust memory and degrade or crash the server by opening many concurrent connections, streams, or sending oversized request bodies. The issue is similar in nature to CVE-2025-47950 (QUIC DoS) but affects additional server types that do not enforce connection limits, stream limits, or message size constraints.

### Impact

#### 1. Missing connection and stream limits (gRPC / HTTPS / HTTP3)

The affected servers do not enforce reasonable upper bounds on concurrent connections or active streams. An attacker can:

- Open many parallel connections
- Rapidly issue requests without limit
- Consume memory until the CoreDNS process becomes unresponsive or is terminated by the OOM killer

Testing demonstrates that modest resource configurations (e.g., 256 MB RAM) can be exhausted quickly. Increasing concurrency parameters in the PoCs allows attackers to scale the impact.

#### 2. Missing message-size validation in the gRPC server

The gRPC server accepts arbitrarily large protobuf messages (default limit ~4 MB per request) without validating against DNS protocol constraints (maximum 64 KB). Sending multiple concurrent oversized messages can quickly exhaust available memory.

This vulnerability mirrors earlier hardening work in PR https://github.com/coredns/coredns/pull/7490, which applied checks for upstream proxying but left server-side request validation unprotected.

#### Result:
In all cases, remote unauthenticated attackers can reliably trigger memory exhaustion and cause a denial of service.


### Patches
_v1.14.0_

## References
- https://github.com/coredns/coredns/security/advisories/GHSA-527x-5wrf-22m2
- https://nvd.nist.gov/vuln/detail/CVE-2025-68151
- https://github.com/coredns/coredns/pull/7490
- https://github.com/coredns/coredns/commit/0d8cbb1a6bcb6bc9c1a489865278b8725fa20812
- https://github.com/coredns/coredns
