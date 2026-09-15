# [M] Envoy vulnerable to crash for scoped ip address during DNS

## Summary
Severity: Medium
Advisory: GHSA-3cw6-2j68-868p
CVE: CVE-2026-26310
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-3cw6-2j68-868p
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/envoy` — affected 1.37.0
- Go: `github.com/envoyproxy/envoy` — affected >=1.36.0
- Go: `github.com/envoyproxy/envoy` — affected >=1.35.0
- Go: `github.com/envoyproxy/envoy` — affected >=0

## Details
### Summary

Calling `Utility::getAddressWithPort` with a scoped IPv6 addresses causes a crash. This utility is called in the data plane from the original_src filter and the dns filter.

### Details

The crashing function is `Utility::getAddressWithPort`. The crash occurs if a string containing a scoped IPv6 address is passed to this function.

This vulnerability affects:

1. The **original src filter**: If the filter is configured and the original source is a scoped IPv6 address, it will cause a crash.
2. **DNS response address resolution**: If a DNS response contains a scoped IPv6 address, this will also trigger the crash.

### PoC

To reproduce the vulnerability:

1. **Method A (Original Src Filter):** Configure the `original src` filter in Envoy and provide a scoped IPv6 address as the original source.
2. **Method B (DNS Resolution):** Trigger a DNS resolution process within Envoy where the DNS response contains a scoped IPv6 address.

### Impact

This is a Denial of Service (DoS) vulnerability. It impacts users who have the `original src` filter configured or whose Envoy instances resolve addresses from DNS responses that may contain scoped IPv6 addresses.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-3cw6-2j68-868p
- https://nvd.nist.gov/vuln/detail/CVE-2026-26310
- https://github.com/envoyproxy/envoy
