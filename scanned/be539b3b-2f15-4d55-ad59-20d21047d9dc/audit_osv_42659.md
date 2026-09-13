# [H] Taubyte Tau v1.1.10 Missing Authorization via POST /projects/{id}

## Summary
Severity: High
Advisory: CVE-2026-69119
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-69119
Type: osv

## Details
Taubyte Tau v1.1.10 contains a missing authorization vulnerability in the services/auth HTTP service that allows any authenticated user to read or permanently delete another tenant's project by supplying an arbitrary project ID to the GET and DELETE /projects/{id} endpoints. The GitHubTokenHTTPAuth middleware only validates that a caller presents a valid GitHub OAuth token without verifying ownership or access rights to the target project, enabling attackers with any valid GitHub token to invoke bare KV-store operations such as projects.Fetch and project.Delete against any project ID to achieve cross-tenant project takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69119.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-69119
- https://www.vulncheck.com/advisories/taubyte-tau-missing-authorization-via-post-projects-id
- https://github.com/taubyte/tau/issues/513
- https://github.com/taubyte/tau/commit/f5c9c9c311a1ff156814e0c81f186bfd101ec237
- https://github.com/taubyte/tau
