# [C] knowns before 0.30.0 Unauthenticated Management API Exposure

## Summary
Severity: Critical
Advisory: CVE-2026-86543
Aliases: GHSA-fc85-99vc-9c75
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-86543
Type: osv

## Details
knowns versions before 0.30.0 serve the management API without authentication on all network interfaces by default, with no password required on fresh installations. Attackers can access the unauthenticated /api/tunnel/start endpoint to provision a public tunnel and republish the API at a publicly accessible address.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86543.json
- https://github.com/knowns-dev/knowns/releases/tag/v0.30.0
- https://github.com/knowns-dev/knowns/security/advisories/GHSA-fc85-99vc-9c75
- https://nvd.nist.gov/vuln/detail/CVE-2026-86543
- https://www.vulncheck.com/advisories/knowns-before-0.30.0-unauthenticated-management-api-exposure
- https://github.com/knowns-dev/knowns/commit/878a02cb7cc14f0a592fdfda7a520af3cac500fb
- https://github.com/knowns-dev/knowns/blob/v0.29.1/internal/cli/browser.go#L193-L200
- https://github.com/knowns-dev/knowns/blob/v0.29.1/internal/server/auth.go#L80-L86
- https://github.com/knowns-dev/knowns/blob/v0.29.1/internal/server/routes/tunnel.go#L26-L38
