# [C] Hermes WebUI < 0.51.311 RCE via Git Configuration Injection

## Summary
Severity: Critical
Advisory: CVE-2026-49959
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-49959
Type: osv

## Details
Hermes WebUI before version 0.51.311 contains a remote code execution vulnerability that allows authenticated attackers to execute arbitrary commands by placing malicious executable Git configuration in a workspace repository's .git/config file. Attackers can exploit Git subprocess invocations in api/workspace_git.py through vectors such as core.fsmonitor during git status, protocol.ext.allow with ext:: remotes during git fetch, credential.helper, core.askPass, core.gitProxy, or inherited environment variables including GIT_SSH_COMMAND to achieve arbitrary command execution on the host running the application.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49959.json
- https://github.com/nesquena/hermes-webui/releases/tag/v0.51.311
- https://nvd.nist.gov/vuln/detail/CVE-2026-49959
- https://www.vulncheck.com/advisories/hermes-webui-rce-via-git-configuration-injection
- https://github.com/nesquena/hermes-webui/pull/3776
- https://github.com/nesquena/hermes-webui/commit/938ac9f55b53def1eefb48c4c42dabaf9c22e99c
- https://github.com/nesquena/hermes-webui
