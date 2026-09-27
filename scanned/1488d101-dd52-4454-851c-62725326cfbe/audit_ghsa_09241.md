# [H] @fastify/accepts-serializer Vulnerable to Denial of Service via Unbounded Accept Header Cache Growth

## Summary
Severity: High
Advisory: GHSA-qxhc-wx3p-2wmg
CVE: CVE-2026-7768
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-qxhc-wx3p-2wmg
Type: github-advisory

## Affected
- npm: `@fastify/accepts-serializer` — affected >=0 <6.0.4

## Details
### Impact

`@fastify/accepts-serializer` cached serializer-selection results keyed by the request `Accept` header without a size limit or eviction policy. A remote unauthenticated client could send many distinct but matching `Accept` header variants to make the cache grow unbounded. Under sustained load, this can exhaust the Node.js heap and crash the process.

### Patches

Update to `@fastify/accepts-serializer >= 6.0.4`. The cache is now bounded by an LRU with a default size of 100 entries, configurable via the new `cacheSize` plugin option.

### Workarounds

None. Upgrade is required.

## References
- https://github.com/fastify/fastify-accepts-serializer/security/advisories/GHSA-qxhc-wx3p-2wmg
- https://nvd.nist.gov/vuln/detail/CVE-2026-7768
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/fastify-accepts-serializer
