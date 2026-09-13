# [H] link-preview-js vulnerable to IPv6 and internal loopback attacks

## Summary
Severity: High
Advisory: GHSA-4gp8-rjrq-ch6q
CVE: CVE-2026-43897
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-4gp8-rjrq-ch6q
Type: github-advisory

## Affected
- npm: `link-preview-js` — affected >=0 <4.0.1

## Details
### Impact
The library did not check for IPv6 loopback attacks. There was also a DNS attack, where an address could be resolved into an internal IP. This could cause internal data leaks.

### Patches
Problem has been patched in version 4.0.1. However, it cannot be completely solved by the package alone. The regex used for validation has been tightened for IPv6 addresses. 

The DNS resolving, however, is more difficult. The regex has been tightened to prohibit .internal, .local, .nip.io and .sslip.io addresses, however there can be other services not on the list, therefore it is imperative that users use the resolveDNSHost option to do DNS resolution before fetching content. To that regard a (scary) error message has been added when the option is not set.

### Workarounds
Users can do their own validation before fetching content.

Reported by https://github.com/Andrew-most-likely

## References
- https://github.com/OP-Engineering/link-preview-js/security/advisories/GHSA-4gp8-rjrq-ch6q
- https://nvd.nist.gov/vuln/detail/CVE-2026-43897
- https://github.com/OP-Engineering/link-preview-js/pull/179
- https://github.com/OP-Engineering/link-preview-js/commit/4396d48909fab37553c0e93e26447fe218363ede
- https://github.com/OP-Engineering/link-preview-js
- https://github.com/OP-Engineering/link-preview-js/releases/tag/4.0.1
