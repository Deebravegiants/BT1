# [M] requests-hardened is Vulnerable to Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-vh75-fwv3-pqrh
CVE: CVE-2026-42175
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-vh75-fwv3-pqrh
Type: github-advisory

## Affected
- PyPI: `requests-hardened` — affected >=0 <1.2.1

## Details
The SSRF protection in `requests-hardened` prior to version 1.2.1 fails to block IP addresses within the RFC 6598 Shared Address Space (`100.64.0.0/10`). An attacker who can supply arbitrary URLs to `requests-hardened` could exploit this gap to access internal services hosted within `100.64.0.0/10`. This is for example relevant in environments such as AWS EKS where `100.64.0.0/10` is commonly used as the default pod CIDR.

The impact is environment-dependent, deployments that utilize the affected CIDR range for internal networking are exposed to SSRF bypass, while others may not be affected.

The issue is resolved in version 1.2.1 by extending the IP filtering logic to explicitly block the RFC 6598 range in addition to standard private addresses, as well as blocking all other reserved addresses (such as multicast) to prevent the re-occurrence of similar issues.

Version 1.2.1 is now blocking the following CIDRs:

- `192.88.99.0/24` - 6to4 relay anycast
- `100.64.0.0/10` - CG-NAT
- `5f00::/16` - IPv6 Segment Routing
- `64:ff9b::/96` - used for IPv6 & IPv4 translation (NAT64)
- `2001:20::/28` - ORCHIDv2 (overlay identifiers)
- `224.0.0.0/4` - multicast
- `ff00::/8` - multicast

## Resources

- https://github.com/python/cpython/issues/119812
- https://github.com/saleor/requests-hardened/commit/b7403f88d3b3689e57435b75b51691a160aaeef5 - the fix itself
- https://github.com/saleor/requests-hardened/commit/a266b3958bb142bca515b3c230fdea19fbda327c - follow up, adding additional support for outdated Python versions (`3.11.9` and `3.10.11` instead of only `3.11.15` and `3.10.20`)
- https://github.com/saleor/requests-hardened/releases/tag/v1.2.1

## References
- https://github.com/saleor/requests-hardened/security/advisories/GHSA-vh75-fwv3-pqrh
- https://nvd.nist.gov/vuln/detail/CVE-2026-42175
- https://github.com/saleor/requests-hardened/commit/a266b3958bb142bca515b3c230fdea19fbda327c
- https://github.com/saleor/requests-hardened/commit/b7403f88d3b3689e57435b75b51691a160aaeef5
- https://github.com/saleor/requests-hardened
- https://github.com/saleor/requests-hardened/releases/tag/v1.2.1
