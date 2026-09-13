# [H] Metabase: Server-Side Template Injection via Notifications Endpoint Leads to RCE

## Summary
Severity: High
Advisory: CVE-2026-27464
Aliases: GHSA-vcj8-rcm8-gfj9
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-02-21
Source: https://osv.dev/vulnerability/CVE-2026-27464
Type: osv

## Details
Metabase is an open-source data analytics platform. In versions prior to 0.57.13 and versions 0.58.x through 0.58.6, authenticated users are able to retrieve sensitive information from a Metabase instance, including database access credentials. During testing, it was confirmed that a low-privileged user can extract sensitive information including database credentials, into the email body via template evaluation. This issue has been fixed in versions 0.57.13 and 0.58.7. To workaround this issue, users can disable notifications in their Metabase instance to disallow access to the vulnerable endpoints.

## References
- https://github.com/metabase/metabase/releases/tag/v0.57.13
- https://github.com/metabase/metabase/releases/tag/v0.58.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27464.json
- https://github.com/metabase/metabase/security/advisories/GHSA-vcj8-rcm8-gfj9
- https://nvd.nist.gov/vuln/detail/CVE-2026-27464
