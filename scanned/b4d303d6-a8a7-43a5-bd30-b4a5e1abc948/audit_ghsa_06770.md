# [M] Micronaut: DefaultHttpClient follows redirects, forwarding Authorization, Cookie, and Proxy-Authorization headers

## Summary
Severity: Medium
Advisory: GHSA-q6gh-6v2r-hjv3
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-q6gh-6v2r-hjv3
Type: github-advisory

## Affected
- Maven: `io.micronaut:micronaut-http-client` — affected >=1.2.8 <3.10.6
- Maven: `io.micronaut:micronaut-http-client` — affected >=4.0.0-M1 <4.10.24
- Maven: `io.micronaut:micronaut-http-client` — affected >=5.0.0-M1 <5.0.1

## Details
### Impact

> DefaultHttpClient follows redirects and forwards Authorization, Cookie, and Proxy-Authorization headers to redirect targets across domain boundaries. The blocklist only filters Host/Connection/TE/CT/CL.
> Additionally, no maximum redirect count exists, enabling infinite loop DoS.
> Affected: DefaultHttpClient.java lines 231-245, 1591, 2071

> Suggested fix: Strip sensitive headers on cross-domain redirects

### Patches
It has been patched for versions: 

For Micronaut 5, versions equal or greater than 5.0.1 >=
For Micronaut 4, versions equal or greater than 4.10.24 >=
For Micronaut 3, versions equal or greater than 3.10.6 >=

### Workarounds
No

### References
Micronaut 5 Patch: https://github.com/micronaut-projects/micronaut-core/commit/9770328999f490bdfbb9e25addd45bf73d4a173a
Micronaut 4 Patch: https://github.com/micronaut-projects/micronaut-core/commit/70cab4b44fbf985faba2846091f2356b5bd70719
Micronaut 3 Patch: https://github.com/micronaut-projects/micronaut-core/commit/64e539736b8168f201d868b02ace50fe14f57418

## References
- https://github.com/micronaut-projects/micronaut-core/security/advisories/GHSA-q6gh-6v2r-hjv3
- https://github.com/micronaut-projects/micronaut-core/commit/64e539736b8168f201d868b02ace50fe14f57418
- https://github.com/micronaut-projects/micronaut-core/commit/70cab4b44fbf985faba2846091f2356b5bd70719
- https://github.com/micronaut-projects/micronaut-core/commit/9770328999f490bdfbb9e25addd45bf73d4a173a
- https://github.com/micronaut-projects/micronaut-core
