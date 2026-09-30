# [M] Default swagger-ui configuration exposes all files in the module

## Summary
Severity: Medium
Advisory: GHSA-62jr-84gf-wmg4
CVE: CVE-2024-22207
CWE: CWE-1188
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-01-16
Source: https://github.com/advisories/GHSA-62jr-84gf-wmg4
Type: github-advisory

## Affected
- npm: `@fastify/swagger-ui` — affected >=2.0.0 <2.1.0

## Details
### Impact

The default configuration of `@fastify/swagger-ui` without `baseDir` set will lead to all files in the module's directory being exposed via http routes served by the module.

### Patches

Update to v2.1.0

### Workarounds

Use  the `baseDir` option

### References

[HackerOne report
](https://hackerone.com/reports/2312369).

## References
- https://github.com/fastify/fastify-swagger-ui/security/advisories/GHSA-62jr-84gf-wmg4
- https://nvd.nist.gov/vuln/detail/CVE-2024-22207
- https://github.com/fastify/fastify-swagger-ui/commit/13d799a2c5f14d3dd5b15892e03bbcbae63ee6f7
- https://github.com/fastify/fastify-swagger-ui
- https://security.netapp.com/advisory/ntap-20240216-0002
