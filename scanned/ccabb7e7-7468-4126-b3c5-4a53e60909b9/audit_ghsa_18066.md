# [H] vLLM has remote code execution vulnerability in the tool call parser for Qwen3-Coder

## Summary
Severity: High
Advisory: GHSA-79j6-g2m3-jgfw
CVE: CVE-2025-9141
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-21
Source: https://github.com/advisories/GHSA-79j6-g2m3-jgfw
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.10.0 <0.10.1.1

## Details
### Summary
An unsafe deserialization vulnerability allows any authenticated user to execute arbitrary code on the server if they are able to get the model to pass the code as an argument to a tool call.

### Details
 vLLM's [Qwen3 Coder tool parser](https://github.com/vllm-project/vllm/blob/main/vllm/entrypoints/openai/tool_parsers/qwen3coder_tool_parser.py) contains a code execution path that uses Python's `eval()` function to parse tool call parameters. This occurs during the parameter conversion process when the parser attempts to handle unknown data types.

This code path is reached when:
1. Tool calling is enabled (`--enable-auto-tool-choice`)
2. The qwen3_coder parser is specified (`--tool-call-parser qwen3_coder`)
3. The parameter type is not explicitly defined or recognized

### Impact
Remote Code Execution via Python's `eval()` function.

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-79j6-g2m3-jgfw
- https://github.com/vllm-project/vllm/pull/21396
- https://github.com/vllm-project/vllm/commit/4594fc3b281713bd3d7634405b4a1393af40d294
- https://github.com/vllm-project/vllm
