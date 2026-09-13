# [H] Frappe File Permissions can by bypassed using certain endpoints

## Summary
Severity: High
Advisory: CVE-2024-27105
Aliases: GHSA-hq5v-q29v-7rcw
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-03-20
Source: https://osv.dev/vulnerability/CVE-2024-27105
Type: osv

## Details
Frappe is a full-stack web application framework. Prior to versions 14.66.3 and 15.16.0, file permission can be bypassed using certain endpoints, granting less privileged users permission to delete or clone a file. Versions 14.66.3 and 15.16.0 contain a patch for this issue. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27105.json
- https://github.com/frappe/frappe/security/advisories/GHSA-hq5v-q29v-7rcw
- https://nvd.nist.gov/vuln/detail/CVE-2024-27105
