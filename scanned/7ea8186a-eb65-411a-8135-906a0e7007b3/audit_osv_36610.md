# [C] OpenProject has Argument Injection on Repository module that allows Arbitrary File Write

## Summary
Severity: Critical
Advisory: CVE-2026-24685
Aliases: GHSA-74p5-9pr3-r6pw
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/CVE-2026-24685
Type: osv

## Details
OpenProject is an open-source, web-based project management software. Versions prior to 16.6.6 and 17.0.2 have an arbitrary file write vulnerability in OpenProject’s repository diff download endpoint (`/projects/:project_id/repository/diff.diff`) when rendering a single revision via git show. By supplying a specially crafted rev value (for example, `rev=--output=/tmp/poc.txt)`, an attacker can inject git show command-line options. When OpenProject executes the SCM command, Git interprets the attacker-controlled rev as an option and writes the output to an attacker-chosen path. As a result, any user with the `:browse_repository` permission on the project can create or overwrite arbitrary files that the OpenProject process user is permitted to write. The written contents consist of git show output (commit metadata and patch), but overwriting application or configuration files still leads to data loss and denial of service, impacting integrity and availability. The issue has been fixed in OpenProject 17.0.2 and 16.6.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24685.json
- https://github.com/opf/openproject/security/advisories/GHSA-74p5-9pr3-r6pw
- https://nvd.nist.gov/vuln/detail/CVE-2026-24685
