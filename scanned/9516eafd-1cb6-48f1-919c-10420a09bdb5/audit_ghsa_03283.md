# [M] Cross-site scripting in @shopify/koa-shopify-auth

## Summary
Severity: Medium
Advisory: GHSA-jqh7-w5pr-cr56
CVE: CVE-2020-8176
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-17
Source: https://github.com/advisories/GHSA-jqh7-w5pr-cr56
Type: github-advisory

## Affected
- npm: `@shopify/koa-shopify-auth` — affected >=3.1.61 <3.1.63

## Details
A cross-site scripting vulnerability exists in koa-shopify-auth v3.1.61-v3.1.62 that allows an attacker to inject JS payloads into the `shop` parameter on the `/shopify/auth/enable_cookies` endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8176
- https://github.com/Shopify/quilt/pull/1455
- https://hackerone.com/reports/881409
