# [C] vLLM allows Remote Code Execution by Pickle Deserialization via AsyncEngineRPCServer() RPC server entrypoints

## Summary
Severity: Critical
Advisory: GHSA-cj47-qj6g-x7r4
CVE: CVE-2024-9053
CWE: CWE-502, CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-cj47-qj6g-x7r4
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0

## Details
vllm-project vllm version 0.6.0 contains a vulnerability in the AsyncEngineRPCServer() RPC server entrypoints. The core functionality run_server_loop() calls the function _make_handler_coro(), which directly uses cloudpickle.loads() on received messages without any sanitization. This can result in remote code execution by deserializing malicious pickle data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9053
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2025-222.yaml
- https://github.com/vllm-project/vllm
- https://huntr.com/bounties/75a544f3-34a3-4da0-b5a3-1495cb031e09
