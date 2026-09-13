# [H] Code Injection in binary-husky/gpt_academic

## Summary
Severity: High
Advisory: CVE-2024-10950
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10950
Type: osv

## Details
In binary-husky/gpt_academic version <= 3.83, the plugin `CodeInterpreter` is vulnerable to code injection caused by prompt injection. The root cause is the execution of user-provided prompts that generate untrusted code without a sandbox, allowing the execution of parts of the LLM-generated code. This vulnerability can be exploited by an attacker to achieve remote code execution (RCE) on the application backend server, potentially gaining full control of the server.

## References
- https://huntr.com/bounties/9abb1617-0c1d-42c7-a647-d9d2b39c6866
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10950.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10950
