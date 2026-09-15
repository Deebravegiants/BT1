# [C] Karmada Dashboard API Unauthorized Access Vulnerability 

## Summary
Severity: Critical
Advisory: GHSA-5qjg-9mjh-4r92
CVE: CVE-2025-62714
CWE: CWE-862
Ecosystem: Go
Published: 2025-10-24
Source: https://github.com/advisories/GHSA-5qjg-9mjh-4r92
Type: github-advisory

## Affected
- Go: `github.com/karmada-io/dashboard` — affected >=0 <0.2.0

## Details
### Impact
This is an authentication bypass vulnerability in the Karmada Dashboard API. The backend API endpoints (e.g., /api/v1/secret, /api/v1/service) did not enforce authentication, allowing unauthenticated users to access sensitive cluster information such as Secrets and Services directly. Although the web UI required a valid JWT for access, the API itself remained exposed to direct requests without any authentication checks. Any user or entity with network access to the Karmada Dashboard service could exploit this vulnerability to retrieve sensitive data.

### Patches
The issue has been fixed in Karmada Dashboard v0.2.0. This release enforces authentication for all API endpoints. Users are strongly advised to upgrade to version v0.2.0 or later as soon as possible.

### Workarounds
If upgrading is not immediately feasible, users can mitigate the risk by:

- Restricting network access to the Karmada Dashboard service using Kubernetes Network Policies, firewall rules, or ingress controls.
- Placing the Dashboard behind a reverse proxy that enforces authentication (e.g., OAuth2 proxy) to add an additional layer of security.

### References
- Karmada Dashboard v0.2.0 Release : https://github.com/karmada-io/dashboard/releases/tag/v0.2.0
- Fix PR #271
- Fix PR #280

## References
- https://github.com/karmada-io/dashboard/security/advisories/GHSA-5qjg-9mjh-4r92
- https://github.com/karmada-io/dashboard/pull/271
- https://github.com/karmada-io/dashboard/pull/280
- https://github.com/karmada-io/dashboard/commit/8457b8bb87725e2371a638ca5a255fd2895c70f1
- https://github.com/karmada-io/dashboard/commit/d2d04909f25e96b4c20fa6b636c398bd1636ee06
- https://github.com/karmada-io/dashboard
- https://github.com/karmada-io/dashboard/releases/tag/v0.2.0
