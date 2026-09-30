# [C] llama.cpp Use-After-Free in RPC GRAPH_RECOMPUTE Handler

## Summary
Severity: Critical
Advisory: CVE-2026-39909
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-39909
Type: osv

## Details
llama.cpp before b8585 contains a use-after-free vulnerability in the RPC server's GRAPH_RECOMPUTE handler that allows unauthenticated remote attackers to achieve arbitrary read and write access by storing a computation graph, freeing referenced buffers, and reclaiming freed memory with attacker-controlled content. Attackers can send RPC requests to trigger re-execution of stored graphs with dangling pointers, enabling full remote code execution without requiring authentication or user interaction.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39909.json
- https://github.com/ggml-org/llama.cpp/releases/tag/b8585
- https://nvd.nist.gov/vuln/detail/CVE-2026-39909
- https://www.vulncheck.com/advisories/llama-cpp-use-after-free-in-rpc-graph-recompute-handler
- https://github.com/ggml-org/llama.cpp/pull/21175
- https://github.com/ggml-org/llama.cpp/commit/389c7d4955ba55c7418afaebf7c23d9ed64ef707
- https://github.com/ggml-org/llama.cpp
