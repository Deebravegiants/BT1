# [H] Pingora vulnerable to cache poisoning via insecure-by-default cache key

## Summary
Severity: High
Advisory: GHSA-f93w-pcj3-rggc
CVE: CVE-2026-2836
CWE: CWE-639
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-f93w-pcj3-rggc
Type: github-advisory

## Affected
- crates.io: `pingora-cache` — affected >=0 <0.8.0

## Details
### Impact
Pingora versions prior to 0.8.0 generated cache keys using only the URI path, excluding critical factors such as the host header. This allows an attacker to poison the cache and serve cross-origin responses to users.

This vulnerability affects users of Pingora's alpha proxy caching feature who relied on the default CacheKey implementation. An attacker could exploit this for cross-tenant data leakage in multi-tenant deployments, or serve malicious content to legitimate users by poisoning shared cache entries.

Note: Cloudflare customers and Cloudflare's CDN infrastructure were not affected by this vulnerability, as Cloudflare's default cache key implementation uses multiple factors to prevent cache key poisoning and never made use of the previously provided default.

### Patches
We strongly suggest users should upgrade to Pingora v.0.8.0 or higher, which removes the default CacheKey implementation.

### Workarounds
Do not rely on the provided CacheKey default, and at minimum use the host / :authority and the upstream peer TLS scheme as part of building the CacheKey, as well as other factors that may apply to the deployment e.g. HTTP method. 

### References
See [CVE-2026-2836](https://cve.org/CVERecord?id=CVE-2026-2836) and the [Cloudflare blog post](https://blog.cloudflare.com/pingora-oss-smuggling-vulnerabilities/) for more details.

### Credits
Disclosed responsibly by Rajat Raghav (@xclow3n) through the Cloudflare [Bug Bounty Program](https://www.cloudflare.com/disclosure/).

## References
- https://github.com/cloudflare/pingora/security/advisories/GHSA-f93w-pcj3-rggc
- https://nvd.nist.gov/vuln/detail/CVE-2026-2836
- https://github.com/cloudflare/pingora
- https://rustsec.org/advisories/RUSTSEC-2026-0035.html
