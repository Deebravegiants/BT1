# [C] EspoCRM vulnerable to authenticated RCE via Formula with path traversal in attachment `sourceId`, exploitable by admin user

## Summary
Severity: Critical
Advisory: CVE-2026-33656
Aliases: GHSA-7922-x7cf-j54x
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-33656
Type: osv

## Details
EspoCRM is an open source customer relationship management application. Prior to version 9.3.4, EspoCRM's built-in formula scripting engine allowing updating attachment's sourceId thus allowing an authenticated admin to overwrite the `sourceId` field on `Attachment` entities. Because `sourceId` is concatenated directly into a file path with no sanitization in `EspoUploadDir::getFilePath()`, an attacker can redirect any file read or write operation to an arbitrary path within the web server's `open_basedir` scope. Version 9.3.4 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33656.json
- https://github.com/espocrm/espocrm/security/advisories/GHSA-7922-x7cf-j54x
- https://nvd.nist.gov/vuln/detail/CVE-2026-33656
