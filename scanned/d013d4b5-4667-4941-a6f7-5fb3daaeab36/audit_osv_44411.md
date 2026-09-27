# [M] Budibase backend-core SSRF via incomplete default blacklist

## Summary
Severity: Medium
Advisory: CVE-2026-82241
Aliases: GHSA-9754-4wm6-3c8r
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82241
Type: osv

## Details
Budibase backend-core (@budibase/backend-core, as used by @budibase/server) omits the shared address space range 100.64.0.0/10 from its default SSRF blacklist (DEFAULT_BLACKLIST) used by REST datasource query previews. When the default blacklist is active (i.e., a self-hosted deployment has not defined BLACKLIST_IPS), an authenticated user with the Builder permission can submit a REST datasource query preview request to POST /api/queries/preview targeting a reachable HTTP(S) service in the 100.64.0.0/10 range, causing the server to send a request to that target and return its response through the preview flow. Per the advisory, no released fix was identified at the time of publication; remediation is to add 100.64.0.0/10 to DEFAULT_BLACKLIST.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-9754-4wm6-3c8r
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82241.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82241
- https://www.vulncheck.com/advisories/budibase-backend-core-ssrf-via-incomplete-default-blacklist
