# [C] Command Injection on OpenProject repositories leads to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-25763
Aliases: GHSA-x37c-hcg5-r5m7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-02-06
Source: https://osv.dev/vulnerability/CVE-2026-25763
Type: osv

## Details
OpenProject is an open-source, web-based project management software. Prior to versions 16.6.7 and 17.0.3, an arbitrary file write vulnerability exists in OpenProject’s repository changes endpoint (/projects/:project_id/repository/changes) when rendering the “latest changes” view via git log. By supplying a specially crafted rev value (for example, rev=--output=/tmp/poc.txt), an attacker can inject git log command-line options. When OpenProject executes the SCM command, Git interprets the attacker-controlled rev as an option and writes the output to an attacker-chosen path. As a result, any user with the :browse_repository permission on the project can create or overwrite arbitrary files that the OpenProject process user is permitted to write. The written contents consist of git log output, but by crafting custom commits the attacker can still upload valid shell scripts, ultimately leading to RCE. The RCE lets the attacker create a reverse shell to the target host and view confidential files outside of OpenProject, such as /etc/passwd. This issue has been patched in versions 16.6.7 and 17.0.3.

## References
- https://github.com/opf/openproject/releases/tag/v16.6.7
- https://github.com/opf/openproject/releases/tag/v17.0.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25763.json
- https://github.com/opf/openproject/security/advisories/GHSA-x37c-hcg5-r5m7
- https://nvd.nist.gov/vuln/detail/CVE-2026-25763
