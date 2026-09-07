# [M] Undici has an unbounded decompression chain in HTTP responses on Node.js Fetch API via Content-Encoding leads to resource exhaustion

## Summary
Severity: Medium
Advisory: GHSA-g9mf-h72j-4rw9
CVE: CVE-2026-22036
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-14
Source: https://github.com/advisories/GHSA-g9mf-h72j-4rw9
Type: github-advisory

## Affected
- npm: `undici` — affected >=7.0.0 <7.18.2
- npm: `undici` — affected >=0 <6.23.0

## Details
### Impact

The `fetch()` API supports chained HTTP encoding algorithms for response content according to RFC 9110 (e.g., Content-Encoding: gzip, br). This is also supported by the undici decompress interceptor.

However, the number of links in the decompression chain is unbounded and the default maxHeaderSize allows a malicious server to insert thousands compression steps leading to high CPU usage and excessive memory allocation.

### Patches

Upgrade to 7.18.2 or 6.23.0.

### Workarounds

It is possible to apply an undici interceptor and filter long `Content-Encoding` sequences manually.

### References

* https://hackerone.com/reports/3456148
* https://github.com/advisories/GHSA-gm62-xv2j-4w53
* https://curl.se/docs/CVE-2022-32206.html

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-g9mf-h72j-4rw9
- https://nvd.nist.gov/vuln/detail/CVE-2026-22036
- https://github.com/nodejs/undici/commit/b04e3cbb569c1596f86c108e9b52c79d8475dcb3
- https://github.com/nodejs/undici
