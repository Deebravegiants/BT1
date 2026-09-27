# [M] parse-server's file creation and deletion bypasses `readOnlyMasterKey` write restriction

## Summary
Severity: Medium
Advisory: GHSA-xfh7-phr7-gr2x
CVE: CVE-2026-30228
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-06
Source: https://github.com/advisories/GHSA-xfh7-phr7-gr2x
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.5.0-alpha.3
- npm: `parse-server` — affected >=0 <8.6.5

## Details
### Impact

The `readOnlyMasterKey` can be used to create and delete files via the Files API (`POST /files/:filename`, `DELETE /files/:filename`). This bypasses the read-only restriction which violates the access scope of the `readOnlyMasterKey`.

Any Parse Server deployment that uses `readOnlyMasterKey` and exposes the Files API is affected. An attacker with access to the `readOnlyMasterKey` can upload arbitrary files or delete existing files.

### Patches

The fix adds permission checks to both the file upload and file delete handlers.

### Workarounds

There is no workaround other than not using `readOnlyMasterKey`, or restricting network access to the Files API endpoints.

### References
 
- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-xfh7-phr7-gr2x
- Fix for Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.0-alpha.3
- Fix for Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.5

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-xfh7-phr7-gr2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-30228
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.5
- https://github.com/parse-community/parse-server/releases/tag/9.5.0-alpha.3
