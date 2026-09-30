# [M] Checkmate: Unauthenticated Access to Unpublished Status Page

## Summary
Severity: Medium
Advisory: CVE-2026-30829
Aliases: GHSA-57xf-wg6w-fjrr
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-07
Source: https://osv.dev/vulnerability/CVE-2026-30829
Type: osv

## Details
Checkmate is an open-source, self-hosted tool designed to track and monitor server hardware, uptime, response times, and incidents in real-time with beautiful visualizations. Prior to version 3.4.0, an unauthenticated information disclosure vulnerability exists in the GET /api/v1/status-page/:url endpoint. The endpoint does not enforce authentication or verify whether a status page is published before returning full status page details. As a result, unpublished status pages and their associated internal data are accessible to any unauthenticated user via direct API requests. This issue has been patched in version 3.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30829.json
- https://github.com/bluewave-labs/Checkmate/security/advisories/GHSA-57xf-wg6w-fjrr
- https://nvd.nist.gov/vuln/detail/CVE-2026-30829
