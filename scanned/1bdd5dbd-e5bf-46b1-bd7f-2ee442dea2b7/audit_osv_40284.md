# [C] Wekan: Shell Injection via Avatar Upload

## Summary
Severity: Critical
Advisory: CVE-2026-52891
Aliases: GHSA-35j7-h385-2q9g
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-52891
Type: osv

## Details
Wekan is open source kanban built with Meteor. Prior to 9.07, Wekan avatar upload functionality embeds user-supplied filenames into paths later passed to child_process.exec() for MIME-type detection. Because models/avatars.js and models/fileValidation.js used a shell command with the avatar filename, shell metacharacters such as backticks and $() in the filename could execute commands on the server. This issue is fixed in version 9.07.

## References
- https://github.com/wekan/wekan/releases/tag/v9.07
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52891.json
- https://github.com/wekan/wekan/security/advisories/GHSA-35j7-h385-2q9g
- https://nvd.nist.gov/vuln/detail/CVE-2026-52891
- https://github.com/wekan/wekan/commit/a4c74a5980e9f778eb444fd346f32aa3d16786a9
