# [C] Himmelblau unset domain configuration can allow any-tenant authentication at first login for remote deployments

## Summary
Severity: Critical
Advisory: CVE-2026-31957
Aliases: GHSA-q746-m2wv-qh4v
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-31957
Type: osv

## Details
Himmelblau is an interoperability suite for Microsoft Azure Entra ID and Intune. From 3.0.0 to before 3.1.0, if Himmelblau is deployed without a configured tenant domain in himmelblau.conf, authentication is not tenant-scoped. In this mode, Himmelblau can accept authentication attempts for arbitrary Entra ID domains by dynamically registering providers at runtime. This behavior is intended for initial/local bootstrap scenarios, but it can create risk in remote authentication environments. This vulnerability is fixed in 3.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31957.json
- https://github.com/himmelblau-idm/himmelblau/security/advisories/GHSA-q746-m2wv-qh4v
- https://nvd.nist.gov/vuln/detail/CVE-2026-31957
