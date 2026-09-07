# [H] Netmaker: Service User with Network Access Can Access config files with WireGuard Private Keys

## Summary
Severity: High
Advisory: GHSA-4hgg-c4rr-6h7f
CVE: CVE-2026-29196
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-4hgg-c4rr-6h7f
Type: github-advisory

## Affected
- Go: `github.com/gravitl/netmaker` — affected >=0 <1.5.0

## Details
A user assigned the platform-user role can retrieve WireGuard private keys of all wireguard configs in a network by calling GET /api/extclients/{network} or GET /api/nodes/{network}. While the Netmaker UI restricts visibility, the API endpoints return full records, including private keys, without filtering based on the requesting user's ownership.

> Credits
> Artem Danilov (Positive Technologies)

## References
- https://github.com/gravitl/netmaker/security/advisories/GHSA-4hgg-c4rr-6h7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-29196
- https://github.com/gravitl/netmaker
- https://github.com/gravitl/netmaker/releases/tag/v1.5.0
