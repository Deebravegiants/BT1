# [H] CVE-2024-25677

## Summary
Severity: High
Advisory: CVE-2024-25677
Aliases: GHSA-4w9v-7h8h-rv8x
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-09
Source: https://osv.dev/vulnerability/CVE-2024-25677
Type: osv

## Details
In Min before 1.31.0, local files are not correctly treated as unique security origins, which allows them to improperly request cross-origin resources. For example, a local file may request other local files through an XML document.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25677.json
- https://github.com/minbrowser/min/security/advisories/GHSA-4w9v-7h8h-rv8x
- https://nvd.nist.gov/vuln/detail/CVE-2024-25677
