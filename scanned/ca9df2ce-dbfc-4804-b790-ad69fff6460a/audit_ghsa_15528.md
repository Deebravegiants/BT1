# [M] Directus vulnerable to SSRF Loopback IP filter bypass

## Summary
Severity: Medium
Advisory: GHSA-68g8-c275-xf2m
CVE: CVE-2024-46990
CWE: CWE-284, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-68g8-c275-xf2m
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <10.13.3
- npm: `directus` — affected >=11.0.0 <11.1.0
- npm: `@directus/api` — affected >=0 <21.0.0
- npm: `@directus/api` — affected >=22.0.0 <22.1.1

## Details
### Impact
If you're relying on blocking access to localhost using the default `0.0.0.0` filter this can be bypassed using other registered loopback devices (like `127.0.0.2` - `127.127.127.127`)

### Workaround
You can block this bypass by manually adding the `127.0.0.0/8` CIDR range which will block access to any `127.X.X.X` ip instead of just `127.0.0.1`.

## References
- https://github.com/directus/directus/security/advisories/GHSA-68g8-c275-xf2m
- https://nvd.nist.gov/vuln/detail/CVE-2024-46990
- https://github.com/directus/directus/commit/4aace0bbe57232e38cd6a287ee475293e46dc91b
- https://github.com/directus/directus/commit/769fa22797bff5a9231599883b391e013f122e52
- https://github.com/directus/directus/commit/8cbf943b65fd4a763d09a5fdbba8996b1e7797ff
- https://github.com/directus/directus/commit/c1f3ccc681595038d094ce110ddeee38cb38f431
- https://github.com/directus/directus
