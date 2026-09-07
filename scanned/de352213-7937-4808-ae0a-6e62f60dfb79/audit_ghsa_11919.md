# [M] league/commonmark has an embed extension allowed_domains bypass

## Summary
Severity: Medium
Advisory: GHSA-hh8v-hgvp-g3f5
CVE: CVE-2026-33347
CWE: CWE-185, CWE-79, CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-hh8v-hgvp-g3f5
Type: github-advisory

## Affected
- Packagist: `league/commonmark` — affected >=2.3.0 <2.8.2

## Details
### Impact

The `DomainFilteringAdapter` in the Embed extension is vulnerable to an allowlist bypass due to a missing hostname boundary assertion in the domain-matching regex. An attacker-controlled domain like `youtube.com.evil` passes the allowlist check when `youtube.com` is an allowed domain.

This enables two attack vectors:

- **SSRF**: The `OscaroteroEmbedAdapter` makes server-side HTTP requests to the embed URL via the `embed/embed` library. A bypassed domain filter causes the server to make outbound requests to an attacker-controlled host, potentially probing internal services or exfiltrating request metadata.
- **XSS**: `EmbedRenderer` outputs the oEmbed response HTML directly into the page with no sanitization. An attacker controlling the bypassed domain can return arbitrary HTML/JavaScript in their oEmbed response, which is rendered verbatim.

Any application using the `Embed` extension and relying on `allowed_domains` to restrict domains when processing untrusted Markdown input is affected.

### Patches

This has been patched in version **2.8.2**. The fix replaces the regex-based domain check with explicit hostname parsing using `parse_url()`, ensuring exact domain and subdomain matching only.

### Workarounds

- Disable the `Embed` extension, or restrict its use to trusted users
- Provide your own domain-filtering implementation of `EmbedAdapterInterface`
- Enable a [Content Security Policy (CSP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) and outbound firewall restrictions

## References
- https://github.com/thephpleague/commonmark/security/advisories/GHSA-hh8v-hgvp-g3f5
- https://nvd.nist.gov/vuln/detail/CVE-2026-33347
- https://github.com/thephpleague/commonmark/commit/59fb075d2101740c337c7216e3f32b36c204218b
- https://github.com/thephpleague/commonmark
- https://github.com/thephpleague/commonmark/releases/tag/2.8.2
