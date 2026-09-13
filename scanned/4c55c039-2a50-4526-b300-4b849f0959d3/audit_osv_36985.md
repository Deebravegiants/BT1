# [M] tfplan2md has Sensitive Value Exposure in Generated Reports

## Summary
Severity: Medium
Advisory: CVE-2026-27640
Aliases: GHSA-5j8r-g94q-2f39
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:H)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27640
Type: osv

## Details
tfplan2md is software for converting Terraform plan JSON files into human-readable Markdown reports. Prior to version 1.26.1, a bug in tfplan2md affected several distinct rendering paths: AzApi resource body properties, AzureDevOps variable groups, Scriban template context variables, and hierarchical sensitivity detection. This caused reports to render values that should have been masked as "(sensitive)" instead. This issue is fixed in v1.26.1. No known workarounds are available.

## References
- https://github.com/oocx/tfplan2md/releases/tag/v1.26.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27640.json
- https://github.com/oocx/tfplan2md/security/advisories/GHSA-5j8r-g94q-2f39
- https://nvd.nist.gov/vuln/detail/CVE-2026-27640
