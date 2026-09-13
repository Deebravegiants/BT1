# [C] Crawl4AI: Multiple Docker API Vulnerabilities - File Write, SSRF, Auth Bypass, XSS, JS Execution

## Summary
Severity: Critical
Advisory: GHSA-365w-hqf6-vxfg
CVE: CVE-2026-56266
CWE: CWE-22, CWE-306, CWE-79, CWE-798, CWE-918, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-365w-hqf6-vxfg
Type: github-advisory

## Affected
- PyPI: `crawl4ai` — affected >=0 <0.8.7

## Details
### Summary

Multiple security vulnerabilities in the Crawl4AI Docker API server affecting endpoints for crawling, markdown/LLM extraction, screenshots, PDFs, webhooks, monitoring, JavaScript execution, and configuration.

### Vulnerabilities

#### 1. Arbitrary File Write via /screenshot and /pdf (CWE-22, CVSS 9.1)

The `output_path` parameter accepts arbitrary filesystem paths with no validation. An attacker can overwrite server files (DoS) or write to any appuser-writable location.

**Fix:** Added `validate_output_path()` restricting writes to `CRAWL4AI_OUTPUT_DIR` (/tmp/crawl4ai-outputs by default). Added Pydantic `field_validator` rejecting `..` traversal sequences.

#### 2. SSRF via Webhook URL (CWE-918, CVSS 8.6)

Webhook URLs in `/crawl/job` and `/llm/job` accept internal/private IPs with no validation, enabling Server-Side Request Forgery against cloud metadata endpoints (169.254.169.254), internal services, and Docker networks.

**Fix:** Added `validate_webhook_url()` with blocklist for RFC 1918, loopback, link-local, cloud metadata IPs and hostnames. Validation at both job submission and send time. Explicit `follow_redirects=False`.

#### 3. Authentication Bypass on Monitor Endpoints (CWE-306, CVSS 6.5)

The monitor router was mounted without `token_dep` dependency, making all monitoring endpoints (including destructive ones like `/monitor/actions/cleanup`) accessible without authentication.

**Fix:** Added `dependencies=[Depends(token_dep)]` to monitor router. Added explicit token check on WebSocket `/monitor/ws` endpoint.

#### 4. Stored XSS in Monitor Dashboard (CWE-79, CVSS 6.1)

URLs and error messages rendered in the monitor dashboard via `innerHTML` without escaping, enabling stored XSS via crafted crawl URLs.

**Fix:** Server-side `html.escape()` on URL and error storage. Client-side `escapeHtml()` wrapper on all `innerHTML` template injections.

#### 5. Arbitrary JavaScript Execution via /execute_js (CWE-94, CVSS 8.1)

The `/execute_js` endpoint accepts and executes arbitrary JavaScript in the server's browser with `--disable-web-security` enabled, combining arbitrary JS execution with SSRF capability.

**Fix:** Disabled by default via `CRAWL4AI_EXECUTE_JS_ENABLED` env var. Added SSRF blocklist on destination URL. Removed `--disable-web-security` from default browser args.

#### 6. Hardcoded JWT Secret Key (CWE-798, CVSS 9.8)

The JWT signing key defaults to `"mysecret"` in the public source code, allowing anyone to forge valid authentication tokens.

**Fix:** Removed default value. Added startup validation rejecting weak/short secrets. Auto-generates ephemeral key when JWT enabled but no key set.

#### 7. SSRF via Direct Crawl Endpoints /crawl, /md, /llm (CWE-918, CVSS 8.6)

The primary crawl entry points (`/crawl`, `/crawl/stream`, `/md`, `/llm`) fetch arbitrary user-supplied URLs with no destination validation, enabling Server-Side Request Forgery against internal services, Docker networks, and cloud metadata endpoints (169.254.169.254). A blocklist that only inspects the literal hostname is additionally bypassable via IPv6-mapped IPv4 addresses (e.g. `[::ffff:169.254.169.254]`, `[::ffff:10.0.0.1]`), which resolve to the blocked private/metadata ranges but evade a naive string check.

**Fix:** Added URL destination validation on all crawl/md/llm entry points, reusing the SSRF blocklist (RFC 1918, loopback, link-local, cloud-metadata IPs and hostnames). IPv6-mapped IPv4 addresses are normalized to their IPv4 form before the blocklist check, closing the mapping bypass. `raw://` URLs are skipped. Validation applies at request entry, not only at fetch time.

### Workarounds

1. Upgrade to the patched version (recommended)
2. Set `CRAWL4AI_API_TOKEN` to enable authentication
3. Set a strong `SECRET_KEY` (min 32 chars) if using JWT
4. Restrict network access to the Docker API

### Credits

- Jeongbean Jeon - file write, SSRF, monitor auth bypass, stored XSS
- wulonchia - file write via output_path (independent report)
- by111 ([August829](https://github.com/August829)) - hardcoded JWT, eval in /config/dump, /execute_js, hook sandbox escape
- secsys_codex - SSRF via /md, /crawl, /llm endpoints + IPv6-mapped IPv4 bypass (URL destination validation)
- Velayutham Selvaraj ([LinkedIn](https://www.linkedin.com/in/velayuthamselvaraj)) - SSRF via missing host validation in validate_url_scheme (independent report)
- IcySun & Yashon - SSRF, arbitrary file write, missing-auth-by-default, hook sandbox bypass via asyncio (independent report)

## References
- https://github.com/unclecode/crawl4ai/security/advisories/GHSA-365w-hqf6-vxfg
- https://nvd.nist.gov/vuln/detail/CVE-2026-56266
- https://www.vulncheck.com/advisories/crawl4ai-unauthenticated-access-to-monitor-endpoints-via-docker-api-server
- https://www.vulncheck.com/advisories/crawl4ai-stored-cross-site-scripting-in-monitor-dashboard
- https://www.vulncheck.com/advisories/crawl4ai-server-side-request-forgery-via-webhook-urls
- https://www.vulncheck.com/advisories/crawl4ai-server-side-request-forgery-via-direct-crawl-endpoints
- https://www.vulncheck.com/advisories/crawl4ai-authentication-bypass-via-hardcoded-jwt-signing-key
- https://www.vulncheck.com/advisories/crawl4ai-arbitrary-javascript-execution-via-execute-js-endpoint
- https://www.vulncheck.com/advisories/crawl4ai-arbitrary-file-write-via-output-path-parameter
- https://github.com/unclecode/crawl4ai
- https://github.com/pypa/advisory-database/tree/main/vulns/crawl4ai/PYSEC-2026-798.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/crawl4ai/PYSEC-2026-596.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/crawl4ai/PYSEC-2026-3449.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/crawl4ai/PYSEC-2026-3443.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/crawl4ai/PYSEC-2026-239.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/crawl4ai/PYSEC-2026-230.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/crawl4ai/PYSEC-2026-229.yaml
- https://github.com/advisories/GHSA-xrfj-6m49-wfmm
- https://github.com/advisories/GHSA-g2pv-76hm-j4x9
- https://github.com/advisories/GHSA-8qrg-7j2f-rf2h
