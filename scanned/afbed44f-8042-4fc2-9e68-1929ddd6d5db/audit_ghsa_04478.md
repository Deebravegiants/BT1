# [H] Crawl4AI: SSRF via proxy settings in the Docker server bypasses the crawl-URL SSRF check

## Summary
Severity: High
Advisory: GHSA-6qhc-x826-342c
CVE: CVE-2026-53755
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-6qhc-x826-342c
Type: github-advisory

## Affected
- PyPI: `crawl4ai` — affected >=0 <0.8.9

## Details
### Summary

The Docker API server applied its SSRF destination check to the crawl target URL only, not to the proxy address. An unauthenticated request could supply a proxy pointing at an internal IP and route the browser through it, reaching internal services and cloud-metadata endpoints, while using a perfectly valid crawl URL. The Docker API is unauthenticated by default.

### Affected paths

`/crawl`, `/crawl/stream`, and `/crawl/job` accept a `browser_config` (and `crawler_config`). The following all feed Chromium's egress and were unchecked:
- `browser_config.proxy_config.server`
- `browser_config.proxy` (deprecated field)
- `crawler_config.proxy_config.server`
- `--proxy-server` / `--proxy-pac-url` / `--proxy-bypass-list` / `--host-resolver-rules` flags in `browser_config.extra_args`

### Attack

An attacker sends `/crawl` with a benign, validation-passing URL but a `proxy_config.server` pointing at an internal IP. Chromium routes all requests through that proxy. For plain-HTTP targets the proxy receives the full request and can return any content, which is then returned verbatim in the crawl result (`results[0].html` / `cleaned_html` / `markdown`). In a real deployment the proxy would be an attacker-controlled server pointing at cloud metadata (e.g. AWS IMDSv1 at 169.254.169.254) to retrieve IAM credential tokens.

### Impact

Unauthenticated server-side request forgery to internal services and cloud-metadata endpoints, with the response returned to the attacker.

### Fix

Every proxy destination is validated with the same global-routability check used for crawl URLs (reject any resolved address that is not `is_global`, including IPv6 transition forms) before the browser is constructed; proxy/DNS-redirecting flags are stripped from `extra_args`. A legitimate public proxy still works. Honors `CRAWL4AI_ALLOW_INTERNAL_URLS`.

### Workarounds

- Upgrade to the patched version (0.8.9).
- Enable authentication (`CRAWL4AI_API_TOKEN`).
- Restrict the container's outbound network access (egress firewall / no metadata route).

### Credits

Geo ([geo-chen](https://github.com/geo-chen)) - reported the proxy_config.server SSRF with a clear PoC.

## References
- https://github.com/unclecode/crawl4ai/security/advisories/GHSA-6qhc-x826-342c
- https://nvd.nist.gov/vuln/detail/CVE-2026-53755
- https://github.com/pypa/advisory-database/tree/main/vulns/crawl4ai/PYSEC-2026-588.yaml
- https://github.com/unclecode/crawl4ai
