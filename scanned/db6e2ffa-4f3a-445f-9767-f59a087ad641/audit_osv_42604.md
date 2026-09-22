# [C] Wekan:hell Injection in External Antivirus Scanner Path via asyncExec

## Summary
Severity: Critical
Advisory: CVE-2026-68560
Aliases: GHSA-x3xm-pxrv-jg7p
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-68560
Type: osv

## Details
Wekan is open source kanban built with Meteor. Prior to 9.75, models/fileValidation.js interpolated the uploaded fileObj.path into the administrator-configured externalCommandLine at its {file} placeholder and executed the result through asyncExec, which is promisify(exec) and invokes `/bin/sh -c`. On deployments with an external scanner configured, an authenticated user able to upload an attachment could place shell metacharacters such as command substitutions in the filename and execute commands as the Wekan server process. Version 9.75 adds shellQuote() and passes the file path as a POSIX single-quoted argument so shell metacharacters cannot escape the placeholder. This issue is fixed in version 9.75.

## References
- https://github.com/wekan/wekan/releases/tag/v9.75
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68560.json
- https://github.com/wekan/wekan/security/advisories/GHSA-x3xm-pxrv-jg7p
- https://nvd.nist.gov/vuln/detail/CVE-2026-68560
- https://github.com/wekan/wekan/commit/1a222c4477e68c76fd6a866954b535fba0a78d05
