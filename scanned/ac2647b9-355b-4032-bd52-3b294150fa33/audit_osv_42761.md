# [M] changedetection.io - Omitted Checkbox in /settings Save Silently Disables API Key Enforcement

## Summary
Severity: Medium
Advisory: CVE-2026-71204
CVSS: 6.2 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71204
Type: osv

## Details
changedetection.io's /settings save handler builds an update dict from form.data['application'] and blind-merges it into the stored application settings via .update.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71204.json
- https://github.com/dgtlmoon/changedetection.io
- https://nvd.nist.gov/vuln/detail/CVE-2026-71204
