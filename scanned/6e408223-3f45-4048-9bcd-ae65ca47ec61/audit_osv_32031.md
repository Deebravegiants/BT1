# [C] Coolify vulnerable to Privilege Escalation resulting in Remote Command Execution (RCE)

## Summary
Severity: Critical
Advisory: CVE-2025-22611
Aliases: GHSA-9w72-9qww-qj6g
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-01-24
Source: https://osv.dev/vulnerability/CVE-2025-22611
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to version 4.0.0-beta.361, the missing authorization allows any authenticated user to escalate his or any other team members privileges to any role, including the owner role. He's also able to kick every other member out of the team, including admins and owners. This allows the attacker to access the `Terminal` feature and execute remote commands. Version 4.0.0-beta.361 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22611.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-9w72-9qww-qj6g
- https://nvd.nist.gov/vuln/detail/CVE-2025-22611
