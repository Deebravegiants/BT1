# [M] WireGuard Easy Weak Token Generation Information Disclosure via OTL Route

## Summary
Severity: Medium
Advisory: CVE-2026-63089
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:L/SA:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-63089
Type: osv

## Details
WireGuard Easy through 15.3.0, fixed in commit 66b292b, contains a cryptographically weak one-time link token generation vulnerability that allows unauthenticated network attackers to recover WireGuard peer credentials by brute-forcing a keyspace of at most 1000 candidate tokens per client ID, as the token is computed using CRC32 over a random value constrained to 0-999. Attackers can enumerate candidate tokens against the unauthenticated /cnf/:oneTimeLink route, which lacks rate limiting and does not validate token expiration, to obtain a peer's PrivateKey and PresharedKey and impersonate that peer on the VPN network.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63089.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63089
- https://www.vulncheck.com/advisories/wireguard-easy-weak-token-generation-information-disclosure-via-otl-route
- https://github.com/wg-easy/wg-easy/pull/2661
- https://github.com/wg-easy/wg-easy/commit/66b292b11bde3664f05ffb016c8082665d261ded
- https://github.com/wg-easy/wg-easy
