# [H] GLPI allows remote code execution through the plugin loader

## Summary
Severity: High
Advisory: CVE-2024-37149
Aliases: GHSA-cwvp-j887-m4xh
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-10
Source: https://osv.dev/vulnerability/CVE-2024-37149
Type: osv

## Details
GLPI is an open-source asset and IT management software package that provides ITIL Service Desk features, licenses tracking and software auditing. An authenticated technician user can upload a malicious PHP script and hijack the plugin loader to execute this malicious script. Upgrade to 10.0.16.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37149.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-cwvp-j887-m4xh
- https://nvd.nist.gov/vuln/detail/CVE-2024-37149
