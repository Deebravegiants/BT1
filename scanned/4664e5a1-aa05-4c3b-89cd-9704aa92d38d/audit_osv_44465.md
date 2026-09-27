# [C] DeepSeek Harness < 0.1.2-alpha.1 Authentication Bypass via Host Header Spoofing

## Summary
Severity: Critical
Advisory: CVE-2026-82533
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-82533
Type: osv

## Details
DeepSeek Harness before 0.1.2-alpha.1 contains an authentication bypass vulnerability that grants unauthenticated access to its local HTTP agent-control API by accepting a client-supplied loopback Host header in place of validating the actual TCP connection origin. On the default configuration, a confined tool-executed process can reach the loopback API without any port exposure and use it to escape its own OS sandbox, escalate to unconfined execution, and disable the approval prompt. When the port is externally reachable via tunnel, SSH forward, or reverse proxy, a remote attacker can exploit the same flaw to create sessions, execute arbitrary commands, and exfiltrate stored conversation transcripts without credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82533.json
- https://github.com/deepseek-ai/deepseek-harness/releases/tag/dsh-v0.1.2-alpha.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-82533
- https://www.vulncheck.com/advisories/deepseek-harness-alpha-1-authentication-bypass-via-host-header-spoofing
- https://github.com/deepseek-ai/deepseek-harness/commit/3e24087bfaeabe40b58ba2f7b936895b8f93fe27
- https://github.com/deepseek-ai/deepseek-harness
- https://www.ox.security/blog/cve-2026-82533-deepseek-harness-ai-agent-sandbox-escape/
