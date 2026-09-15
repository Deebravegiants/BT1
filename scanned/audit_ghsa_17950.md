# [M] elysia-cors Origin Validation Error

## Summary
Severity: Medium
Advisory: GHSA-f9qj-4c5x-cpcw
CVE: CVE-2025-50864
CWE: CWE-178, CWE-346
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-08-20
Source: https://github.com/advisories/GHSA-f9qj-4c5x-cpcw
Type: github-advisory

## Affected
- npm: `@elysiajs/cors` — affected >=0 <1.3.1

## Details
An Origin Validation Error in the elysia-cors library thru 1.3.0 allows attackers to bypass Cross-Origin Resource Sharing (CORS) restrictions. The library incorrectly validates the supplied origin by checking if it is a substring of any domain in the site's CORS policy, rather than performing an exact match. For example, a malicious origin like "notexample.com", "example.common.net" is whitelisted when the site's CORS policy specifies "example.com." This vulnerability enables unauthorized access to user data on sites using the elysia-cors library for CORS validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-50864
- https://github.com/elysiajs/elysia-cors/commit/9b9eb92e32a7a4b43b6d5108668941701c33e221
- https://github.com/elysiajs/elysia-cors
- https://github.com/elysiajs/elysia-cors/blob/main/src/index.ts
- https://github.com/elysiajs/elysia-cors/tree/main
- https://medium.com/@raghavagrawal_23036/cors-bypass-in-popular-opensource-library-ad27fb41e16a
- http://elysiajs.com
