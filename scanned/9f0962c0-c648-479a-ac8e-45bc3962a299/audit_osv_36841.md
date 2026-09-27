# [M] Sentry allows unauthorized access to event data across organizational boundaries

## Summary
Severity: Medium
Advisory: CVE-2026-26004
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-03-17
Source: https://osv.dev/vulnerability/CVE-2026-26004
Type: osv

## Details
Sentry is a developer-first error tracking and performance monitoring tool. Versions prior to 26.1.0 have a cross-organization Insecure Direct Object Reference (IDOR) vulnerability in Sentry's GroupEventJsonView endpoint. Version 26.1.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26004.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26004
- https://securitylab.github.com/advisories/GHSL-2025-130_Sentry/
- https://github.com/getsentry/sentry/commit/45bc78fd57514a04eb62e73dd1eeb3ca2d723997
- https://github.com/getsentry/sentry/pull/105601
