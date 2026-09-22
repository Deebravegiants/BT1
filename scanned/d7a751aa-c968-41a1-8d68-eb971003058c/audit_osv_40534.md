# [M] Coturn: Arbitrary File Write via CLI psd Command

## Summary
Severity: Medium
Advisory: CVE-2026-53449
Aliases: GHSA-jj76-vwjw-w34r
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-53449
Type: osv

## Details
Coturn is a free open source implementation of TURN and STUN Server. Prior to 4.13.0, the psd print sessions dump CLI command in coturn takes a filename argument and directly passes it to fopen with no path validation. An authenticated admin with CLI access can overwrite arbitrary files writable by the coturn process because the command string is used as-is after stripping the psd prefix and leading spaces, allowing truncation and overwrite with session dump data. This issue is fixed in version 4.13.0.

## References
- https://github.com/coturn/coturn/releases/tag/4.13.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53449.json
- https://github.com/coturn/coturn/security/advisories/GHSA-jj76-vwjw-w34r
- https://nvd.nist.gov/vuln/detail/CVE-2026-53449
- https://github.com/coturn/coturn/commit/e72930f571beba3bc7a9f97661af2614aae92a55
