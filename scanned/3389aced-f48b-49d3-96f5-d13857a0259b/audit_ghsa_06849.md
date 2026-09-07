# [M] safeurl is Missing IPv6 CIDR Ranges in Blocklist

## Summary
Severity: Medium
Advisory: GHSA-xgch-x3mx-cm3c
CVE: CVE-2026-54452
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-xgch-x3mx-cm3c
Type: github-advisory

## Affected
- Go: `github.com/doyensec/safeurl` — affected >=0 <0.2.4

## Details
The `privateNetworks` blocklist was found to be missing newly added CIDR ranges. More specifically, the following CIDR ranges were not being blocked:
- `64:ff9b:1::/48`: NAT64 local-use prefix (RFC 8215)
- `5f00::/16`: Segment Routing (SRv6) SIDs (RFC 9602)
- `3fff::/20`: documentation prefix (RFC 9637)
- `100:0:0:1::/64`: Dummy IPv6 Prefix (RFC 9780)

### Impact
If exploited, an attacker would potentially be able to reach resources hosted on the IPs residing in the missing ranges.

### Workarounds
Disable IPv6 by setting `EnableIPv6(false)`. This is the default behavior of the library.

### Resolution
Upgrade to v0.2.4

### Credits
safeurl thanks @tonghuaroot for reporting.

## References
- https://github.com/doyensec/safeurl/security/advisories/GHSA-xgch-x3mx-cm3c
- https://github.com/doyensec/safeurl
- https://github.com/doyensec/safeurl/releases/tag/v0.2.4
