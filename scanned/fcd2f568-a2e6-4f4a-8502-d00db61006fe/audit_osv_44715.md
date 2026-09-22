# [M] git-mcp-server 2.15.1 Argument Injection via Git Ref Parameters

## Summary
Severity: Medium
Advisory: CVE-2026-85626
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85626
Type: osv

## Details
git-mcp-server 2.15.1 contains an argument injection vulnerability in the ref and object parameters of git_log, git_diff, and git_show tools that lack leading-dash validation. Attackers can inject git command-line options like --output= to write files outside the repository to arbitrary paths accessible by the process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85626.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85626
- https://www.vulncheck.com/advisories/git-mcp-server-2.15.1-argument-injection-via-git-ref-parameters
- https://github.com/cyanheads/git-mcp-server/issues/53
- https://github.com/cyanheads/git-mcp-server
- https://github.com/cyanheads/git-mcp-server/blob/v2.15.3/src/services/git/providers/cli/operations/commits/log.ts
- https://github.com/cyanheads/git-mcp-server/blob/v2.15.3/src/services/git/providers/cli/utils/command-builder.ts
