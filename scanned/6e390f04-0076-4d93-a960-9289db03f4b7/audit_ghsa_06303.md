# [H] http4k: Unbounded gzip decompression in `ServerFilters.GZip` / `RequestFilters.GunZip` allowed memory-exhaustion DoS

## Summary
Severity: High
Advisory: GHSA-g4w2-6h2r-3m3w
CVE: CVE-2026-53659
CWE: CWE-409
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-g4w2-6h2r-3m3w
Type: github-advisory

## Affected
- Maven: `org.http4k:http4k-core` — affected >=6.0.0.0 <6.49.0.0
- Maven: `org.http4k:http4k-core` — affected >=5.0.0.0 <5.42.0.0
- Maven: `org.http4k:http4k-core` — affected >=0

## Details
### Impact

`ServerFilters.GZip` and `RequestFilters.GunZip` (and the underlying `Gzip` functions used to decompress request bodies) did not impose any cap on the decompressed size. A small malicious gzip-encoded request body (on the order of kilobytes) could decompress to gigabytes, exhausting the JVM heap and denying service to other clients.

**Who is affected:** any http4k server that accepts gzip-encoded requests via `ServerFilters.GZip` or `RequestFilters.GunZip`. Exploitable by any unauthenticated client. The vulnerability was introduced on 2017-08-01 (commit `2618fe08f9`) and was present for ~9 years.

### Patches

| Line | Fixed in | Edition |
|------|----------|---------|
| v6.x (Community) | **6.49.0.0** | Community |
| v5.x (LTS) | **5.42.0.0** | Enterprise — contact [enterprise@http4k.org](mailto:enterprise@http4k.org) |
| v4.x (LTS) | **4.51.0.0** | Enterprise — contact [enterprise@http4k.org](mailto:enterprise@http4k.org) |

The fix caps decompression at 10MB by default; oversized requests through `ServerFilters.GZip` / `RequestFilters.GunZip` now return `413 Request Entity Too Large`, and decompressing elsewhere throws `SizeLimitExceededException`. The keyed `hmacSHA256` helper and other safe paths are unaffected.

### Workarounds

For deployments that cannot upgrade immediately:
- Replace the `GZip` / `GunZip` filters with custom versions that wrap the decompressed `InputStream` in a size-limited reader, or
- Strip gzip-encoded request support at the edge (CDN, reverse proxy, or load balancer).

### References

- Vulnerability introduced: [`2618fe08f9`](https://github.com/http4k/http4k/commit/2618fe08f9)
- Fix release: [v6.49.0.0](https://github.com/http4k/http4k/releases/tag/6.49.0.0)
- Background: [CWE-409 — Improper Handling of Highly Compressed Data](https://cwe.mitre.org/data/definitions/409.html)

## References
- https://github.com/http4k/http4k/security/advisories/GHSA-g4w2-6h2r-3m3w
- https://github.com/http4k/http4k
- https://github.com/http4k/http4k/releases/tag/6.49.0.0
