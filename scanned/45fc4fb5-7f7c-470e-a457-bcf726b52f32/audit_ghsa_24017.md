# [M] Diavante vue-storefront-api and storefront-api disclose stack trace

## Summary
Severity: Medium
Advisory: GHSA-9wxj-37p8-49ff
CVE: CVE-2020-11883
CWE: CWE-200, CWE-209
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9wxj-37p8-49ff
Type: github-advisory

## Affected
- npm: `storefront-api` — affected >=0 <1.0.0-rc3
- npm: `vue-storefront-api` — affected >=0 <1.12.0

## Details
In Divante vue-storefront-api through 1.11.1 and storefront-api through 1.0-rc.1, as used in VueStorefront PWA, unexpected HTTP requests lead to an exception that discloses the error stack trace, with absolute file paths and Node.js module names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11883
- https://github.com/DivanteLtd/storefront-api/pull/59
- https://github.com/DivanteLtd/vue-storefront-api/pull/431
- https://github.com/vuestorefront/storefront-api/commit/9165b80c72b469c9615ce2f665499e6f6ead0a6a
- https://github.com/vuestorefront/vue-storefront-api/commit/965247f41f872e84e4662d04d8e2108eaf6119da
