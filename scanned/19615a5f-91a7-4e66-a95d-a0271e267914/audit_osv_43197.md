# [H] Rainbond 6.9.7 Region API Cross-Enterprise IDOR via Tenant Access

## Summary
Severity: High
Advisory: CVE-2026-72741
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-72741
Type: osv

## Details
Rainbond through 6.9.7 contains a broken access control vulnerability in the CheckToken function that allows authenticated attackers to access unauthorized enterprise resources by substituting another enterprise's tenant name in URL paths. Attackers can use any valid API token to bypass enterprise ID verification and access or modify another enterprise's services, plugins, environment variables, and certificates.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72741.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72741
- https://www.vulncheck.com/advisories/rainbond-region-api-cross-enterprise-idor-via-tenant-access
- https://github.com/goodrain/rainbond/issues/2665
- https://github.com/goodrain/rainbond
