# [M] Undici has an HTTP Request/Response Smuggling issue

## Summary
Severity: Medium
Advisory: GHSA-2mjp-6q6p-2qxm
CVE: CVE-2026-1525
CWE: CWE-444
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-2mjp-6q6p-2qxm
Type: github-advisory

## Affected
- npm: `undici` — affected >=0 <6.24.0
- npm: `undici` — affected >=7.0.0 <7.24.0

## Details
### Impact

Undici allows duplicate HTTP `Content-Length` headers when they are provided in an array with case-variant names (e.g., `Content-Length` and `content-length`). This produces malformed HTTP/1.1 requests with multiple conflicting `Content-Length` values on the wire.

**Who is impacted:**
  - Applications using `undici.request()`, `undici.Client`, or similar low-level APIs with headers passed as flat arrays
  - Applications that accept user-controlled header names without case-normalization

**Potential consequences:**
  - **Denial of Service**: Strict HTTP parsers (proxies, servers) will reject requests with duplicate `Content-Length` headers (400 Bad Request)
  - **HTTP Request Smuggling**: In deployments where an intermediary and backend interpret duplicate headers inconsistently (e.g., one uses the first value, the other uses the last), this can enable request smuggling attacks leading to ACL bypass, cache poisoning, or credential hijacking

### Patches

 Patched in the undici version v7.24.0 and v6.24.0. Users should upgrade to this version or later.

### Workarounds

  If upgrading is not immediately possible:

  1. **Validate header names**: Ensure no duplicate `Content-Length` headers (case-insensitive) are present before passing headers to undici
  2. **Use object format**: Pass headers as a plain object (`{ 'content-length': '123' }`) rather than an array, which naturally deduplicates by key
  3. **Sanitize user input**: If headers originate from user input, normalize header names to lowercase and reject duplicates

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-2mjp-6q6p-2qxm
- https://nvd.nist.gov/vuln/detail/CVE-2026-1525
- https://hackerone.com/reports/3556037
- https://cna.openjsf.org/security-advisories.html
- https://cwe.mitre.org/data/definitions/444.html
- https://github.com/nodejs/undici
- https://www.rfc-editor.org/rfc/rfc9110.html#section-8.6
