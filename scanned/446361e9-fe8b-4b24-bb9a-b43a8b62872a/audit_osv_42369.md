# [M] OpenCost < 1.121.0 Unauthenticated Helm Values Exposure and Admin Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-67349
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-67349
Type: osv

## Details
OpenCost before 1.121.0 fails to authenticate the GET /helmValues endpoint, exposing base64-decoded HELM_VALUES environment variable containing cloud provider credentials. Additionally, adminAuthMiddleware fails open when ADMIN_TOKEN is unset, allowing unauthenticated attackers to modify GCP service account keys via POST /serviceKey to redirect billing calls.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67349.json
- https://github.com/opencost/opencost/releases/tag/core/v1.121.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-67349
- https://www.vulncheck.com/advisories/opencost-unauthenticated-helm-values-exposure-and-admin-bypass
- https://github.com/opencost/opencost/issues/3893
- https://github.com/opencost/opencost/commit/a49a25bc2e0d6e220a131a4dc58f38ebe6ae851b
- https://github.com/opencost/opencost/pull/3910
- https://github.com/opencost/opencost
