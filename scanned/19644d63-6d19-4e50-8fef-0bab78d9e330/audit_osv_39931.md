# [H] KanaDojo < 0.1.18 Sandbox Escape RCE via messages.cjs

## Summary
Severity: High
Advisory: CVE-2026-48546
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-48546
Type: osv

## Details
KanaDojo before 0.1.18 contains a sandbox escape vulnerability that allows an attacker to execute arbitrary code by exploiting the explicit passing of the global require function into a Node.js vm.runInNewContext() sandbox context in the issue-auto-respond.yml workflow. Attackers can submit a pull request modifying messages.cjs to import arbitrary Node.js modules, bypassing sandbox restrictions and achieving remote code execution with full GitHub Actions runner privileges including access to AUTOMATION_PR_TOKEN.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48546.json
- https://github.com/lingdojo/kana-dojo/releases/tag/v0.1.18
- https://nvd.nist.gov/vuln/detail/CVE-2026-48546
- https://www.vulncheck.com/advisories/kanadojo-sandbox-escape-rce-via-messages-cjs
- https://github.com/lingdojo/kana-dojo/commit/31b85a5d7c4b323ddeba3b2dc5e7807558710544
- https://github.com/lingdojo/kana-dojo
