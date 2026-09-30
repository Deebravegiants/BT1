# [C] Dokploy: OS Command Injection via SSH-form `customGitUrl` domain in `ssh-keyscan`

## Summary
Severity: Critical
Advisory: CVE-2026-72740
Aliases: GHSA-6693-xv3f-69px
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72740
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, packages/server/src/utils/providers/git.ts parses the user-controlled customGitUrl with sanitizeRepoPathSSH and interpolates its domain into the ssh-keyscan command from addHostToKnownHostsCommand without shell quoting, allowing an authenticated member with service deployment permission and an attached SSH key to execute arbitrary commands on the Dokploy host during deployment. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72740.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-6693-xv3f-69px
- https://nvd.nist.gov/vuln/detail/CVE-2026-72740
- https://github.com/Dokploy/dokploy/commit/47347ab885b0ad1f5d0ef0e5e74bbba35c7f93bc
