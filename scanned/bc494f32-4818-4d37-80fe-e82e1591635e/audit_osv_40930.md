# [M] Capgo - Broken Object Level Authorization in Build Job Control via jobId Parameter

## Summary
Severity: Medium
Advisory: CVE-2026-56231
Aliases: GHSA-72j4-9qp5-hfrg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-56231
Type: osv

## Details
Capgo before 12.128.2 contains a broken object level authorization (BOLA) vulnerability in the POST /build/start/:jobId and POST /build/cancel/:jobId endpoints. The handlers authorize the request based only on the attacker-controlled app_id supplied in the request body and never verify that the jobId in the URL belongs to that app_id (or the same tenant/org) before issuing privileged builder commands with the server-held builder API key. An authenticated user with the app.build_native permission for any app they control can start or cancel arbitrary builder jobs belonging to other tenants by supplying a victim jobId, resulting in cross-tenant build sabotage (denial of service), unauthorized compute actions, and potential billing impact.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56231.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-72j4-9qp5-hfrg
- https://nvd.nist.gov/vuln/detail/CVE-2026-56231
- https://www.vulncheck.com/advisories/capgo-broken-object-level-authorization-in-build-job-control-via-jobid-parameter
