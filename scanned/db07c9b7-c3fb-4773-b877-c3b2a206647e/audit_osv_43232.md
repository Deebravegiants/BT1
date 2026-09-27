# [C] Dokploy: Command Injection via Unescaped Git URL in Clone Commands

## Summary
Severity: Critical
Advisory: CVE-2026-72874
Aliases: GHSA-hrfh-82jj-3q46
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72874
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, cloneGitRepository in packages/server/src/utils/providers/git.ts interpolates customGitUrl and customGitBranch into a git clone command passed to execAsync or execAsyncRemote, allowing an authenticated user with application access to execute arbitrary operating system commands on the Dokploy host by setting a malicious custom Git URL and triggering deployment. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72874.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-hrfh-82jj-3q46
- https://nvd.nist.gov/vuln/detail/CVE-2026-72874
- https://github.com/Dokploy/dokploy/commit/47347ab885b0ad1f5d0ef0e5e74bbba35c7f93bc
- https://github.com/Dokploy/dokploy/pull/4855
