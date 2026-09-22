# [H] Checkmate: Sensitive Bearer Token Exposure via Public Status Pages When showURL Setting is Enabled

## Summary
Severity: High
Advisory: CVE-2026-71862
Aliases: GHSA-3m74-8cg9-rp8j
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-71862
Type: osv

## Details
Checkmate is an open-source, self-hosted tool designed to track and monitor server hardware, uptime, response times, and incidents in real-time with beautiful visualizations. From 3.3.0 until 3.9.2, enabling the global showURL setting causes the unauthenticated GET /api/v1/status-page/:url endpoint to return complete monitor objects from server/src/controllers/statusPageController.ts. The response includes the secret field used by HttpProvider.ts as an HTTP Authorization credential, even though BaseStatusPage.tsx does not display that value, allowing visitors to extract credentials from the JSON response and use them against monitored services. This issue is fixed in version 3.9.2.

## References
- https://github.com/bluewave-labs/Checkmate/releases/tag/v3.9.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71862.json
- https://github.com/bluewave-labs/Checkmate/security/advisories/GHSA-3m74-8cg9-rp8j
- https://nvd.nist.gov/vuln/detail/CVE-2026-71862
- https://github.com/bluewave-labs/Checkmate/commit/cc1814f507041bb0f64845bed5d5442c21e920f2
- https://github.com/bluewave-labs/Checkmate/pull/3758
