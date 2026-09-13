# [C] Dokku: OS Command Injection via App Name in Git Pre-Receive Hook

## Summary
Severity: Critical
Advisory: CVE-2026-45408
Aliases: GHSA-9x85-7gxq-fcr3
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-45408
Type: osv

## Details
Dokku is a docker-powered PaaS. Prior to 0.38.2, the app name validation regex (^[a-z0-9][^/:_A-Z]*$) permits shell metacharacters. When an authenticated user pushes to a git remote with a crafted app name, the name is embedded unquoted into a bash pre-receive hook script via an unquoted heredoc (<<EOF instead of <<'EOF') in fn-git-create-hook() at plugins/git/internal-functions:378. On git push, bash interprets the semicolon as a command separator, executing arbitrary commands as the dokku user. This vulnerability is fixed in 0.38.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45408.json
- https://github.com/dokku/dokku/security/advisories/GHSA-9x85-7gxq-fcr3
- https://nvd.nist.gov/vuln/detail/CVE-2026-45408
- https://github.com/dokku/dokku/pull/8590
