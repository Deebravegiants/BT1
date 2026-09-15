# [C] Seahub < 13.0.23 - Authentication Bypass in ShareLinkZipTaskView GET Method

## Summary
Severity: Critical
Advisory: CVE-2026-56768
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-56768
Type: osv

## Details
Seahub before 13.0.23 does not enforce SHARE_LINK_LOGIN_REQUIRED on GET /api/v2.1/share-link-zip-task/, allowing unauthenticated users to bypass authentication. Attackers with a folder share-link token can call the GET endpoint to obtain a fileserver zip token and download entire shared directory trees.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56768.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56768
- https://plus.seafile.com/wiki/publish/seafile-wiki/v5D5/
- https://www.vulncheck.com/advisories/seahub-authentication-bypass-in-sharelinkziptaskview-get-method
- https://github.com/haiwen/seahub/issues/9050
- https://github.com/haiwen/seahub/commit/162cddae0831188d02bb8d451dc2193e197dcc57
- https://github.com/haiwen/seahub/commit/b609949cf64ed6a15708d0fb5ea9c179962e23cc
- https://github.com/haiwen/seahub
