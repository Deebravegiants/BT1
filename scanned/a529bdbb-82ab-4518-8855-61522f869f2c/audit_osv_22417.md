# [H] Command Injection/Argument Injection in GoCD

## Summary
Severity: High
Advisory: CVE-2022-29184
Aliases: GHSA-vf5r-r7j2-cf2h
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-20
Source: https://osv.dev/vulnerability/CVE-2022-29184
Type: osv

## Details
GoCD is a continuous delivery server. In GoCD versions prior to 22.1.0, it is possible for existing authenticated users who have permissions to edit or create pipeline materials or pipeline configuration repositories to get remote code execution capability on the GoCD server via configuring a malicious branch name which abuses Mercurial hooks/aliases to exploit a command injection weakness. An attacker would require access to an account with existing GoCD administration permissions to either create/edit (`hg`-based) configuration repositories; create/edit pipelines and their (`hg`-based) materials; or, where "pipelines-as-code" configuration repositories are used, to commit malicious configuration to such an external repository which will be automatically parsed into a pipeline configuration and (`hg`) material definition by the GoCD server. This issue is fixed in GoCD 22.1.0. As a workaround, users who do not use/rely upon Mercurial materials can uninstall/remove the `hg`/Mercurial binary from the underlying GoCD Server operating system or Docker image.

## References
- https://github.com/gocd/gocd/releases/tag/22.1.0
- https://www.gocd.org/releases/#22-1-0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29184.json
- https://github.com/gocd/gocd/security/advisories/GHSA-vf5r-r7j2-cf2h
- https://nvd.nist.gov/vuln/detail/CVE-2022-29184
- https://github.com/gocd/gocd/commit/37d35115db2ada2190173f9413cfe1bc6c295ecb
