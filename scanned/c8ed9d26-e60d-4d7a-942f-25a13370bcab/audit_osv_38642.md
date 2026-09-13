# [H] Squidex has SSRF via Backup Restore Endpoint — Admin-Controlled URL Download Allows Internal and External Requests

## Summary
Severity: High
Advisory: CVE-2026-41170
Aliases: GHSA-6q6m-7h5j-jq4g
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-41170
Type: osv

## Details
Squidex is an open source headless content management system and content management hub. Prior to version 7.23.0, the `RestoreController.PostRestoreJob` endpoint allows an administrator to supply an arbitrary URL for downloading backup archives. This URL is fetched using the "Backup" `HttpClient` without any SSRF protection. A malicious or compromised admin can use this endpoint to probe internal network services, access cloud metadata endpoints, or perform internal reconnaissance. The vulnerability is authenticated (Admin-only) but highly impactful, allowing potential access to sensitive internal resources. Version 7.23.0 contains a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41170.json
- https://github.com/Squidex/squidex/security/advisories/GHSA-6q6m-7h5j-jq4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-41170
- https://github.com/Squidex/squidex/commit/b81d75e1d9c1a8e30993c2ee59b350002b9aeda4
