# [C] SiYuan before 3.8.2 Remote Code Execution via Clipboard

## Summary
Severity: Critical
Advisory: CVE-2026-86712
Aliases: GHSA-9rr9-pxr4-gcgc
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86712
Type: osv

## Details
SiYuan before 3.8.2 trusts the attacker-writable text/siyuan clipboard MIME type and skips sanitization in the paste handler, allowing code execution in the Node-enabled desktop renderer. Attackers can craft malicious web pages that write to the clipboard, and when pasted into SiYuan, injected scripts execute with full Node.js access through the Electron main process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86712.json
- https://github.com/siyuan-note/siyuan/releases/tag/v3.8.2
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-9rr9-pxr4-gcgc
- https://nvd.nist.gov/vuln/detail/CVE-2026-86712
- https://www.vulncheck.com/advisories/siyuan-before-3.8.2-remote-code-execution-via-clipboard
- https://github.com/siyuan-note/siyuan/commit/9ce660652de2ced26ec2d98a5a242cb0b8bb7273
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/blob/v3.8.1/app/src/protyle/util/paste.ts
