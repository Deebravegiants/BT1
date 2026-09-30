# [C] Coolify Command Injection Vulnerability in Project Name

## Summary
Severity: Critical
Advisory: CVE-2025-22606
Aliases: GHSA-ccp8-v65g-m526
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P)
Published: 2025-01-24
Source: https://osv.dev/vulnerability/CVE-2025-22606
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. In version 4.0.0-beta.358 and possibly earlier versions, when creating or updating a "project," it is possible to inject arbitrary shell commands by altering the project name. If a name includes unescaped characters, such as single quotes (`'`), it breaks out of the intended command structure, allowing attackers to execute arbitrary commands on the host system. This vulnerability allows attackers to execute arbitrary commands on the host server, which could result in full system compromise; create, modify, or delete sensitive system files; and escalate privileges depending on the permissions of the executed process. Attackers with access to project management features could exploit this flaw to gain unauthorized control over the host environment. Version 4.0.0-beta.359 fixes this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22606.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-ccp8-v65g-m526
- https://nvd.nist.gov/vuln/detail/CVE-2025-22606
