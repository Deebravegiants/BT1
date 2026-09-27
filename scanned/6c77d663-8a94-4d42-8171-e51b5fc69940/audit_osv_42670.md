# [H] radare2 < 6.1.4 Project Deletion Path Traversal Directory Deletion

## Summary
Severity: High
Advisory: CVE-2026-6940
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-6940
Type: osv

## Details
radare2 prior to 6.1.4 contains a path traversal vulnerability in project deletion that allows local attackers to recursively delete arbitrary directories by supplying absolute paths that escape the configured dir.projects root directory. Attackers can craft absolute paths to project marker files outside the project storage boundary to cause recursive deletion of attacker-chosen directories with permissions of the radare2 process, resulting in integrity and availability loss.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6940.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6940
- https://www.vulncheck.com/advisories/radare2-project-deletion-path-traversal-directory-deletion
- https://github.com/radareorg/radare2/pull/25830
- https://github.com/radareorg/radare2/pull/25830/commits
