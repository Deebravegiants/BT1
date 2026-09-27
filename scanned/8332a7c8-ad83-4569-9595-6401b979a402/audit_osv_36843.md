# [M] Redos (Regular Expression Denial of Service) at Code Extraction Block in significant-gravitas/autogpt

## Summary
Severity: Medium
Advisory: CVE-2026-26006
Aliases: GHSA-m2wr-7m3r-p52c
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-10
Source: https://osv.dev/vulnerability/CVE-2026-26006
Type: osv

## Details
AutoGPT is a platform that allows users to create, deploy, and manage continuous artificial intelligence agents that automate complex workflows. The autogpt before 0.6.32 is vulnerable to Regular Expression Denial of Service due to the use of regex at Code Extraction Block. The two Regex are used containing the corresponding dangerous patterns \s+[\s\S]*? and \s+(.*?). They share a common characteristic — the combination of two adjacent quantifiers that can match the same space character (\s). As a result, an attacker can supply a long sequence of space characters to trigger excessive regex backtracking, potentially leading to a Denial of Service (DoS). This vulnerability is fixed in 0.6.32.

## References
- https://github.com/Significant-Gravitas/AutoGPT/blob/master/autogpt_platform/backend/backend/blocks/code_extraction_block.py#L106-L109
- https://github.com/Significant-Gravitas/AutoGPT/blob/master/autogpt_platform/backend/backend/blocks/code_extraction_block.py#L86-L96
- https://github.com/Significant-Gravitas/AutoGPT/releases/tag/autogpt-platform-beta-v0.6.32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26006.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-m2wr-7m3r-p52c
- https://nvd.nist.gov/vuln/detail/CVE-2026-26006
- https://github.com/Significant-Gravitas/AutoGPT/commit/57a06f70883ce6be18738c6ae8bb41085c71e266
