# [M] Capgo - Authorization Bypass in App Ownership Transfer via Direct PostgREST Update

## Summary
Severity: Medium
Advisory: CVE-2026-56257
Aliases: GHSA-v9jp-r5wh-qqcp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-56257
Type: osv

## Details
Capgo before 12.128.2 allows direct patching of public.apps.owner_org through PostgREST, bypassing the transfer_app() workflow and creating split-brain ownership. Attackers can directly update apps.owner_org while leaving app_versions.owner_org unchanged, enabling old-org keys to retain access to version data while new-org keys control the app record.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56257.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-v9jp-r5wh-qqcp
- https://nvd.nist.gov/vuln/detail/CVE-2026-56257
- https://www.vulncheck.com/advisories/capgo-authorization-bypass-in-app-ownership-transfer-via-direct-postgrest-update
