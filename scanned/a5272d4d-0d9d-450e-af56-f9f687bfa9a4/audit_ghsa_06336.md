# [H] GeoLens's authorization and cache-scope flaws disclose private dataset data and metadata to unauthorized users (fixed in 1.2.4)

## Summary
Severity: High
Advisory: GHSA-p77j-g7h5-r2vw
CWE: CWE-1021, CWE-1392, CWE-200, CWE-285, CWE-400, CWE-524, CWE-532, CWE-918, CWE-93
Ecosystem: PyPI
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-p77j-g7h5-r2vw
Type: github-advisory

## Affected
- PyPI: `geolens` — affected >=0 <1.2.4

## Details
GeoLens 1.2.4 fixes a set of vulnerabilities, the most serious of which allow authenticated or anonymous users to obtain data and metadata for datasets they are not authorized to access.

### Impact

- **Private record metadata disclosure.** Record contact, keyword, and distribution sub-resource endpoints did not re-authorize the backing dataset, so any authenticated user could read a private record's contact details (PII), keywords, and distributions. (Runtime-proven.)
- **Private tile data via shared caches.** Private raster and vector tiles were served with shared-cache (`Cache-Control: public`) headers, so a shared cache (a CDN or the bundled reverse proxy) could retain private tile bytes and replay them to later unauthenticated requests, including unpublished public-dataset previews.
- **Private dataset title enumeration.** The map visibility-check endpoint did not authorize read access to the map, allowing any editor to enumerate the titles of non-public datasets in any map by ID — including private maps owned by other users.
- **SSRF via DNS rebinding.** URL validation for user-supplied service URLs (probes, STAC/OGC API sources, manifest downloads) resolved DNS once and then let the HTTP client re-resolve at connect time, allowing a low-TTL domain to pass validation as a public address and connect to an internal/metadata address.
- **Token leak + header injection in service preview.** The remote-service preview path passed the authorization token to GDAL via the process environment without sanitization, leaking it through `/proc/<pid>/environ` and allowing CRLF header injection.
- **Unauthenticated STAC search DoS.** `POST /search` did not cap the size of GeoJSON `intersects` geometries (the `GET` sibling did).
- **API key written to access logs.** The bundled reverse proxy logged the `api_key` query-string credential in cleartext.
- **Security posture coupled to a logging flag.** API documentation exposure and the Secure flag on the OAuth session cookie were keyed off the `LOG_JSON` logging flag rather than an explicit environment setting, so a production deployment at the default could expose `/docs` and emit a non-Secure session cookie.
- **Missing Content-Security-Policy (defense-in-depth).** The web application shipped no `script-src`/`default-src` CSP, leaving no containment for token exfiltration if an XSS issue were introduced.
- **Weak default install credentials.** The installer kept the published default database password and could silently retain the default admin password on a headless install.

### Patches

Upgrade to **GeoLens 1.2.4**. No configuration changes are required for the authorization and cache fixes. Operators on a public, TLS-terminated deployment should additionally set `ENVIRONMENT=production` to make the production security posture explicit; deployments that do not set it retain their prior behavior.

### Workarounds

None for the authorization/cache disclosure flaws — upgrading is required. The SSRF and STAC-DoS surfaces can be partially mitigated at the network/proxy layer (egress filtering to block link-local metadata addresses; a request-size limit on `POST /search`), but the code fix is the durable remedy.

### References

- Release: https://github.com/geolens-io/geolens/releases/tag/v1.2.4
- Pull request: https://github.com/geolens-io/geolens/pull/243
- Prior related advisory: GHSA-p23g-mvhj-jh3j

## References
- https://github.com/geolens-io/geolens/security/advisories/GHSA-p77j-g7h5-r2vw
- https://github.com/geolens-io/geolens/pull/243
- https://github.com/advisories/GHSA-p23g-mvhj-jh3j
- https://github.com/geolens-io/geolens
- https://github.com/geolens-io/geolens/releases/tag/v1.2.4
