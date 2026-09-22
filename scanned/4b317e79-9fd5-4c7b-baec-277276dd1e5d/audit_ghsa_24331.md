# [C] Command injection in workspace-tools

## Summary
Severity: Critical
Advisory: GHSA-5875-m6jq-vf78
CVE: CVE-2022-25865
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-5875-m6jq-vf78
Type: github-advisory

## Affected
- npm: `workspace-tools` — affected >=0 <0.18.4

## Details
The package workspace-tools before 0.18.4 is vulnerable to Command Injection via git argument injection. When calling the fetchRemoteBranch(remote: string, remoteBranch: string, cwd: string) function, both the remote and remoteBranch parameters are passed to the git fetch subcommand in a way that additional flags can be set. The additional flags can be used to perform a command injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25865
- https://github.com/microsoft/workspace-tools/pull/103
- https://github.com/microsoft/workspace-tools/commit/9bc7e65ce497f87e1f363fd47b8f802f3d3cd978
- https://github.com/microsoft/workspace-tools
- https://snyk.io/vuln/SNYK-JS-WORKSPACETOOLS-2421201
