# [C] AIT-DSN < 2.2.2 Missing Authentication via SLE API Routes

## Summary
Severity: Critical
Advisory: CVE-2026-60113
Aliases: GHSA-gj83-67wr-82mv
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-60113
Type: osv

## Details
AMMOS Instrument Toolkit (AIT) Deep Space Network (DSN) Interface before 2.2.2 contains a missing authentication vulnerability in the Space Link Extension (SLE) interface manager that allows unauthenticated network attackers to access seven unprotected API routes by sending direct HTTP requests with no credentials. Attackers can reach the exposed SLE endpoints to start or stop Deep Space Network communication sessions, retrieve telemetry frame data, and inject arbitrary frames into active spacecraft links.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60113.json
- https://github.com/NASA-AMMOS/AIT-DSN/releases/tag/2.2.2
- https://github.com/NASA-AMMOS/AIT-DSN/security/advisories/GHSA-gj83-67wr-82mv
- https://nvd.nist.gov/vuln/detail/CVE-2026-60113
- https://www.vulncheck.com/advisories/ait-dsn-missing-authentication-via-sle-api-routes
- https://github.com/NASA-AMMOS/AIT-DSN/blob/master/CHANGELOG.md#222---2026-07-13
- https://github.com/NASA-AMMOS/AIT-DSN/commit/06d07d1a525602c62c6eaeaeff2544196f430340
- https://github.com/NASA-AMMOS/AIT-DSN
