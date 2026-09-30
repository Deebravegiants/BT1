# [C] Hermes Agent 0.18.2 - 0.21.0 RCE via git core.fsmonitor Config Injection

## Summary
Severity: Critical
Advisory: CVE-2026-71963
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-71963
Type: osv

## Details
Hermes Agent 0.18.2 through 0.21.0, fixed in commit f6234d0, contains a remote code execution vulnerability that allows attackers to execute arbitrary OS commands by supplying a malicious repository with a crafted .git/config that sets core.fsmonitor to an attacker-controlled command. When a user opens the malicious repository and sends any message, the agent triggers a git status index refresh which executes the injected command in the user's process context, exposing the full environment including configured provider API keys.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71963.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71963
- https://www.vulncheck.com/advisories/hermes-agent-rce-via-git-core-fsmonitor-config-injection
- https://github.com/NousResearch/hermes-agent/pull/101483
- https://github.com/NousResearch/hermes-agent/commit/f6234d00c5d59450adea1d7edd30ad3859375c79
- https://github.com/NousResearch/hermes-agent
- https://www.manifold.security/blog/ai-coding-agents-git-hijack
