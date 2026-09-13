# [H] Git Repository Disclosure in Onedev

## Summary
Severity: High
Advisory: CVE-2022-39208
Aliases: GHSA-h427-rv56-c9h2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-13
Source: https://osv.dev/vulnerability/CVE-2022-39208
Type: osv

## Details
Onedev is an open source, self-hosted Git Server with CI/CD and Kanban. All files in the /opt/onedev/sites/ directory are exposed and can be read by unauthenticated users. This directory contains all projects, including their bare git repos and build artifacts. This file disclosure vulnerability can be used by unauthenticated attackers to leak all project files of any project. Since project IDs are incremental, an attacker could iterate through them and leak all project data. This issue has been resolved in version 7.3.0 and users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39208.json
- https://github.com/theonedev/onedev/security/advisories/GHSA-h427-rv56-c9h2
- https://nvd.nist.gov/vuln/detail/CVE-2022-39208
- https://github.com/theonedev/onedev/commit/8aa94e0daf8447cdf76d4f27bfda0a85a7ea5822
- https://blog.sonarsource.com/onedev-remote-code-execution/
