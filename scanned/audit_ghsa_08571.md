# [M] vllm has Improper Resource Shutdown or Release 

## Summary
Severity: Medium
Advisory: GHSA-98f3-hwg4-4rf7
CVE: CVE-2026-9540
CWE: CWE-404
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-98f3-hwg4-4rf7
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0

## Details
A vulnerability was identified in vllm-project vllm 0.19.0. This issue affects some unknown processing of the component OpenAI-compatible Serving Path. Such manipulation leads to denial of service. It is possible to launch the attack remotely. The exploit is publicly available and might be used. The pull request to fix this issue awaits acceptance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9540
- https://github.com/vllm-project/vllm/issues/37343
- https://github.com/vllm-project/vllm/pull/37594
- https://github.com/vllm-project/vllm
- https://ingero.io/debugging-vllm-latency-minimax-ollama-mcp
- https://vuldb.com/submit/814645
- https://vuldb.com/vuln/365601
- https://vuldb.com/vuln/365601/cti
