# [H] Remote Code Execution in BerriAI/litellm

## Summary
Severity: High
Advisory: CVE-2024-6825
Aliases: GHSA-53gh-p8jc-7rg8, PYSEC-2026-1541
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-6825
Type: osv

## Details
BerriAI/litellm version 1.40.12 contains a vulnerability that allows remote code execution. The issue exists in the handling of the 'post_call_rules' configuration, where a callback function can be added. The provided value is split at the final '.' mark, with the last part considered the function name and the remaining part appended with the '.py' extension and imported. This allows an attacker to set a system method, such as 'os.system', as a callback, enabling the execution of arbitrary commands when a chat response is processed.

## References
- https://huntr.com/bounties/1d98bebb-6cf4-46c9-87c3-d3b1972973b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6825.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6825
- https://github.com/berriai/litellm/commit/441c7275ed2715f47650a7c2e525055c804073a9
