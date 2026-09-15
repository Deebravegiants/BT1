# [M] MS-Agent vulnerable to Command Injection

## Summary
Severity: Medium
Advisory: GHSA-4gc2-344q-r2rw
CVE: CVE-2026-2256
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-4gc2-344q-r2rw
Type: github-advisory

## Affected
- PyPI: `ms-agent` — affected >=0

## Details
A Command Injection vulnerability in ModelScope's MS-Agent versions v1.6.0rc1 and earlier exists, allowing an attacker to execute arbitrary operating system commands through crafted prompt-derived input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2256
- https://github.com/Itamar-Yochpaz/CVE-2026-2256-PoC
- https://github.com/modelscope/ms-agent
- https://medium.com/@itamar.yochpaz/cve-2026-2256-from-ai-prompt-to-full-system-compromise-a4114c718326
- https://www.hiddenlayer.com/research/indirect-prompt-injection-of-claude-computer-use
- https://www.kb.cert.org/vuls/id/431821
