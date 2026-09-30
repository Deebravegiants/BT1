# [C] Zero-Click Indirect Prompt Injection and Authentication Bypass via Email Polling

## Summary
Severity: Critical
Advisory: CVE-2026-33654
Aliases: GHSA-4gmr-2vc8-7qh3
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-33654
Type: osv

## Details
nanobot is a personal AI assistant. Prior to version 0.1.6, an indirect prompt injection vulnerability exists in the email channel processing module (`nanobot/channels/email.py`), allowing a remote, unauthenticated attacker to execute arbitrary LLM instructions (and subsequently, system tools) without any interaction from the bot owner. By sending an email containing malicious prompts to the bot's monitored email address, the bot automatically polls, ingests, and processes the email content as highly trusted input, fully bypassing channel isolation and resulting in a stealthy, zero-click attack. Version 0.1.6 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33654.json
- https://github.com/HKUDS/nanobot/security/advisories/GHSA-4gmr-2vc8-7qh3
- https://nvd.nist.gov/vuln/detail/CVE-2026-33654
