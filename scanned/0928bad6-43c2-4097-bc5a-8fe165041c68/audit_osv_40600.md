# [M] Emlog Blind SQL Injection via Authentication Cookie

## Summary
Severity: Medium
Advisory: CVE-2026-53756
Aliases: GHSA-xq97-53c2-vvfg
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-53756
Type: osv

## Details
Emlog is an open source website building system. Prior to version 2.6.16, Emlog CMS Pro contains a blind SQL injection in User_Model::getUserDataByLogin(). The $account parameter is directly interpolated into SQL queries without any filtering. The vulnerability is reachable through the auth cookie validation path, where $username is extracted from the cookie and passed unfiltered into SQL — guarded only by an HMAC signature that requires AUTH_KEY to forge. This issue has been patched in version 2.6.16.

## References
- https://github.com/emlog/emlog/releases/tag/pro-2.6.16
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53756.json
- https://github.com/emlog/emlog/security/advisories/GHSA-xq97-53c2-vvfg
- https://nvd.nist.gov/vuln/detail/CVE-2026-53756
- https://github.com/emlog/emlog/commit/92b6eea618891b28ed0c520564dff26e170645b4
