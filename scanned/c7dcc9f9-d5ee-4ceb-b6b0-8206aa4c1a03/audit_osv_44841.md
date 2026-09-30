# [M] Snipe-IT 8.6.3 Authorization Bypass via Asset Update Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-86765
Aliases: GHSA-6g2g-83pc-6365
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86765
Type: osv

## Details
Snipe-IT versions before 8.7.0 fail to enforce checkout authorization when assignment fields are submitted to the asset update endpoint. Authenticated users with edit permission but explicitly denied checkout permission can reassign assets, bypass check-in procedures, and alter custody records by submitting assigned_user, assigned_asset, or assigned_location parameters to PATCH /api/v1/hardware/{id}.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86765.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-6g2g-83pc-6365
- https://nvd.nist.gov/vuln/detail/CVE-2026-86765
- https://www.vulncheck.com/advisories/snipe-it-8.6.3-authorization-bypass-via-asset-update-endpoint
- https://github.com/grokability/snipe-it/commit/f71806b1e0efbd3bc2b6be61994ad2a5d5d6c206
