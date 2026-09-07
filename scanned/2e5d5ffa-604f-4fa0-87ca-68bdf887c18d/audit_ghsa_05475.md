# [C] Crawl4AI Has Local File Inclusion in Docker API via file:// URLs

## Summary
Severity: Critical
Advisory: GHSA-vx9w-5cx4-9796
CVE: CVE-2026-26217
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-vx9w-5cx4-9796
Type: github-advisory

## Affected
- PyPI: `Crawl4AI` — affected >=0 <0.8.0

## Details
A local file inclusion vulnerability exists in the Crawl4AI Docker API. The /execute_js, /screenshot, /pdf, and /html endpoints accept file:// URLs, allowing attackers to read arbitrary files from the server filesystem.

Attack Vector:
```json
POST /execute_js
{
    "url": "file:///etc/passwd",
    "scripts": ["document.body.innerText"]
}
```
Impact

An unauthenticated attacker can:
- Read sensitive files (/etc/passwd, /etc/shadow, application configs)
- Access environment variables via /proc/self/environ
- Discover internal application structure
- Potentially read credentials and API keys

Workarounds

1. Disable the Docker API
2. Add authentication to the API
3. Use network-level filtering

## References
- https://github.com/unclecode/crawl4ai/security/advisories/GHSA-vx9w-5cx4-9796
- https://nvd.nist.gov/vuln/detail/CVE-2026-26217
- https://github.com/pypa/advisory-database/tree/main/vulns/crawl4ai/PYSEC-2026-34.yaml
- https://github.com/unclecode/crawl4ai
- https://github.com/unclecode/crawl4ai/blob/main/docs/blog/release-v0.8.0.md
- https://github.com/unclecode/crawl4ai/blob/release/v0.8.0/docs/blog/release-v0.8.0.md
- https://github.com/unclecode/crawl4ai/blob/release/v0.8.0/docs/migration/v0.8.0-upgrade-guide.md
- https://www.vulncheck.com/advisories/crawl4ai-docker-api-local-file-inclusion-via-file-url-handling
