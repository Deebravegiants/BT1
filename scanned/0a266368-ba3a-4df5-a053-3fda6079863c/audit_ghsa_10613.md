# [C] Netmaker does not verify JWT signatures for host tokens

## Summary
Severity: Critical
Advisory: GHSA-qpv2-rwc8-c993
CVE: CVE-2026-38651
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-qpv2-rwc8-c993
Type: github-advisory

## Affected
- Go: `github.com/gravitl/netmaker` — affected >=0 <1.5.0

## Details
Netmaker by Gravitl is an open-source WireGuard-based networking platform for creating and managing virtual overlay networks. The `VerifyHostToken` function in `logic/jwts.go` does not validate the JWT signature when verifying host tokens. After calling `jwt.ParseWithClaims`, the function only checks whether the returned token object is non-nil. It does not check `token.Valid` or the returned error. An attacker can forge a JWT signed with any key, set the claims to any host ID, and pull that host's full configuration including bcrypt-hashed passwords, MQTT credentials, and WireGuard peer data. The issue was patched in v1.5.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-38651
- https://github.com/gravitl/netmaker/commit/5309aa70d464ef565911369714d661a61481a79b
- https://github.com/gravitl/netmaker
- https://www.zyenra.com/advisories/netmaker-jwt-verification-bypass
