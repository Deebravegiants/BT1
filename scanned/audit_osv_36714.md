# [H] FileRise affected by an Unauthenticated File Read Due to Insufficient Access Control

## Summary
Severity: High
Advisory: CVE-2026-25231
Aliases: GHSA-hv99-77cw-hvpr
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-25231
Type: osv

## Details
FileRise is a self-hosted web file manager / WebDAV server. Versions prior to 3.3.0, the application contains an unauthenticated file read vulnerability due to the lack of access control on the /uploads directory. Files uploaded to this directory can be accessed directly by any user who knows or can guess the file path, without requiring authentication. As a result, sensitive data could be exposed, and privacy may be breached. This vulnerability is fixed in 3.3.0.

## References
- https://github.com/error311/FileRise/releases/tag/v3.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25231.json
- https://github.com/error311/FileRise/security/advisories/GHSA-hv99-77cw-hvpr
- https://nvd.nist.gov/vuln/detail/CVE-2026-25231
