# [H] Miniflare vulnerable to Server-Side Request Forgery (SSRF)

## Summary
Severity: High
Advisory: GHSA-fwvg-2739-22v7
CVE: CVE-2023-7078
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2023-12-29
Source: https://github.com/advisories/GHSA-fwvg-2739-22v7
Type: github-advisory

## Affected
- npm: `miniflare` — affected >=3.20230821.0 <3.20231030.2

## Details
### Impact
Sending specially crafted HTTP requests to Miniflare's server could result in arbitrary HTTP and WebSocket requests being sent from the server. If Miniflare was configured to listen on external network interfaces (as was the default in `wrangler` until `3.19.0`), an attacker on the local network could access other local servers.

### Patches
The issue was fixed in `miniflare@3.20231030.2`.

### Workarounds
Ensure Miniflare is configured to listen on just local interfaces. This is the default behaviour, but can also be configured with the `host: "127.0.0.1"` option.

### References
- https://github.com/cloudflare/workers-sdk/pull/4532

## References
- https://github.com/cloudflare/workers-sdk/security/advisories/GHSA-fwvg-2739-22v7
- https://nvd.nist.gov/vuln/detail/CVE-2023-7078
- https://github.com/cloudflare/workers-sdk/pull/4532
- https://github.com/cloudflare/workers-sdk
