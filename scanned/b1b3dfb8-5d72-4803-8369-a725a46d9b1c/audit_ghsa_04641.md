# [M] Nokogiri: Possible Out-of-Bounds Read in `Nokogiri::XML::NodeSet#[]`

## Summary
Severity: Medium
Advisory: GHSA-5prr-v3j2-97mh
CWE: CWE-125, CWE-190
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-5prr-v3j2-97mh
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.19.4

## Details
### Summary

`Nokogiri::XML::NodeSet#[]` (and its alias `#slice`) checked the requested index against the node set's bounds using a 32-bit-truncated copy of the index. A large negative index could pass the check and then be used at full width, reading outside the node set's storage. On CRuby this is an out-of-bounds read that typically crashes the process; on JRuby it is not memory-unsafe but returns an incorrect node.

Nokogiri 1.19.4 performs the bounds check against the full-width index.

### Severity

The Nokogiri maintainers have evaluated this as medium severity.

Exploitation requires an application to pass an attacker-controlled integer to `NodeSet#[]`. The primary impact is a controlled crash (denial of service), with potential for memory disclosure on CRuby.

On JRuby, Nokogiri is not affected by this vulnerability.

### Mitigation

Upgrade to Nokogiri 1.19.4 or later.

As a workaround, applications that index a `NodeSet` with externally-supplied integers can validate the index against `node_set.length` before use, or avoid passing untrusted values as an index.

### Credit

This issue was responsibly reported by Zheng Yu from depthfirst.com.

## References
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-5prr-v3j2-97mh
- https://github.com/sparklemotion/nokogiri
