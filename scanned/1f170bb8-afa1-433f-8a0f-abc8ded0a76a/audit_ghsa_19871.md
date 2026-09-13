# [H] Nuxt allows DOS via cache poisoning with payload rendering response

## Summary
Severity: High
Advisory: GHSA-jvhm-gjrh-3h93
CVE: CVE-2025-27415
CWE: CWE-349
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-19
Source: https://github.com/advisories/GHSA-jvhm-gjrh-3h93
Type: github-advisory

## Affected
- npm: `nuxt` — affected >=3.0.0 <3.16.0

## Details
### Summary

By sending a crafted HTTP request to a server behind an CDN, it is possible in some circumstances to poison the CDN cache and highly impacts the availability of a site.

It is possible to craft a request, such as `https://mysite.com/?/_payload.json` which will be rendered as JSON. If the CDN in front of a Nuxt site ignores the query string when determining whether to cache a route, then this JSON response could be served to future visitors to the site.

### Impact

An attacker can perform this attack to a vulnerable site in order to make a site unavailable indefinitely. It is also possible in the case where the cache will be reset to make a small script to send a request each X seconds (=caching duration) so that the cache is permanently poisoned making the site completely unavailable.


## Conclusion : 

This is similar to a vulnerability in Next.js that resulted in CVE-2024-46982 (and see [this article](https://zhero-web-sec.github.io/research-and-things/nextjs-cache-and-chains-the-stale-elixir), in particular the "Internal URL parameter and pageProps" part, the latter being very similar to the one concerning us here.)

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-jvhm-gjrh-3h93
- https://nvd.nist.gov/vuln/detail/CVE-2025-27415
- https://github.com/nuxt/nuxt
