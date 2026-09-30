# [M] webpack-dev-server vulnerable to cross-origin source code exposure on non-HTTPS origins

## Summary
Severity: Medium
Advisory: GHSA-79cf-xcqc-c78w
CVE: CVE-2026-6402
CWE: CWE-749
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-79cf-xcqc-c78w
Type: github-advisory

## Affected
- npm: `webpack-dev-server` — affected >=0 <5.2.4

## Details
### Impact

When webpack-dev-server is running on a non-HTTPS origin (the default), cross-origin requests from malicious websites can load the dev server's JavaScript bundles via `<script>` tags. The fix introduced in v5.2.1 (CVE-2025-30359) relied on `Sec-Fetch-Mode` and `Sec-Fetch-Site` request headers to block these requests, but browsers only send these headers for [potentially trustworthy origins](https://w3c.github.io/webappsec-secure-contexts/#is-origin-trustworthy). Over plain HTTP, the headers are absent and the check is bypassed.

An attacker who knows the dev server's host, port, and output path can exfiltrate all module source code by intercepting the webpack runtime's module registration.

This does not affect Chrome 142+ (and other Chromium-based browsers) due to [local network access restrictions](https://developer.chrome.com/release-notes/142#local_network_access_restrictions).

### Patches

Patched in webpack-dev-server >= 5.2.4 by setting `Cross-Origin-Resource-Policy: same-origin` on responses.

### Workarounds

Run the dev server with HTTPS enabled (`--https` or `server.type: 'https'` in config).

### Resources

- [GHSA-4v9v-hfq4-rm2v](https://github.com/webpack/webpack-dev-server/security/advisories/GHSA-4v9v-hfq4-rm2v) (CVE-2025-30359) - original vulnerability
- [GHSA-9jgg-88mc-972h](https://github.com/webpack/webpack-dev-server/security/advisories/GHSA-9jgg-88mc-972h) (CVE-2025-30360) - prior bypass

## References
- https://github.com/webpack/webpack-dev-server/security/advisories/GHSA-4v9v-hfq4-rm2v
- https://github.com/webpack/webpack-dev-server/security/advisories/GHSA-79cf-xcqc-c78w
- https://github.com/webpack/webpack-dev-server/security/advisories/GHSA-9jgg-88mc-972h
- https://nvd.nist.gov/vuln/detail/CVE-2026-6402
- https://cna.openjsf.org/security-advisories.html
- https://github.com/webpack/webpack-dev-server
