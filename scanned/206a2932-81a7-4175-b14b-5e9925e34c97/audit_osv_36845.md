# [C] Catalyst Affected by Remote Code Execution as Root via Containerized Install Script Execution

## Summary
Severity: Critical
Advisory: CVE-2026-26009
Aliases: GHSA-xv5r-cpcw-8wr3
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-02-10
Source: https://osv.dev/vulnerability/CVE-2026-26009
Type: osv

## Details
Catalyst is a platform built for enterprise game server hosts, game communities, and billing panel integrations. Install scripts defined in server templates execute directly on the host operating system as root via bash -c, with no sandboxing or containerization. Any user with template.create or template.update permission can define arbitrary shell commands that achieve full root-level remote code execution on every node machine in the cluster. This vulnerability is fixed in commit 11980aaf3f46315b02777f325ba02c56b110165d.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26009.json
- https://github.com/karutoil/catalyst/security/advisories/GHSA-xv5r-cpcw-8wr3
- https://nvd.nist.gov/vuln/detail/CVE-2026-26009
- https://github.com/karutoil/catalyst/commit/11980aaf3f46315b02777f325ba02c56b110165d
