# [H] ERPNext: Server-Side Template Injection (SSTI) in Batch autonaming via Stock Settings.naming_series_prefix

## Summary
Severity: High
Advisory: CVE-2026-55242
Aliases: GHSA-pxf3-4gvc-v45j
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-55242
Type: osv

## Details
ERPNext is a free and open source Enterprise Resource Planning tool. Prior to 15.111.0 and 16.22.0, an authenticated user with a standard operational role can trigger server-side template injection through a configuration field, resulting in unauthorized disclosure of data outside the user's normal permission scope. This issue is fixed in versions 15.111.0 and 16.22.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55242.json
- https://github.com/frappe/erpnext/security/advisories/GHSA-pxf3-4gvc-v45j
- https://nvd.nist.gov/vuln/detail/CVE-2026-55242
