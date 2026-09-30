# [M] vLLM has a Regular Expression Denial of Service (ReDoS, Exponential Complexity) Vulnerability in `pythonic_tool_parser.py`

## Summary
Severity: Medium
Advisory: CVE-2025-48887
Aliases: GHSA-w6q7-j642-7c25, PYSEC-2025-50
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-30
Source: https://osv.dev/vulnerability/CVE-2025-48887
Type: osv

## Details
vLLM, an inference and serving engine for large language models (LLMs), has a Regular Expression Denial of Service (ReDoS) vulnerability in the file `vllm/entrypoints/openai/tool_parsers/pythonic_tool_parser.py` of versions 0.6.4 up to but excluding 0.9.0. The root cause is the use of a highly complex and nested regular expression for tool call detection, which can be exploited by an attacker to cause severe performance degradation or make the service unavailable. The pattern contains multiple nested quantifiers, optional groups, and inner repetitions which make it vulnerable to catastrophic backtracking. Version 0.9.0 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48887.json
- https://github.com/vllm-project/vllm/security/advisories/GHSA-w6q7-j642-7c25
- https://nvd.nist.gov/vuln/detail/CVE-2025-48887
- https://github.com/vllm-project/vllm/commit/4fc1bf813ad80172c1db31264beaef7d93fe0601
- https://github.com/vllm-project/vllm/pull/18454
