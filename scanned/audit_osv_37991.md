# [C] llama.cpp: Unauthenticated RCE via GRAPH_COMPUTE buffer=0 bypass in llama.cpp RPC backend

## Summary
Severity: Critical
Advisory: CVE-2026-34159
Aliases: GHSA-j8rj-fmpv-wcxw
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-34159
Type: osv

## Details
llama.cpp is an inference of several LLM models in C/C++. Prior to version b8492, the RPC backend's deserialize_tensor() skips all bounds validation when a tensor's buffer field is 0. An unauthenticated attacker can read and write arbitrary process memory via crafted GRAPH_COMPUTE messages. Combined with pointer leaks from ALLOC_BUFFER/BUFFER_GET_BASE, this gives full ASLR bypass and remote code execution. No authentication required, just TCP access to the RPC server port. This issue has been patched in version b8492.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34159.json
- https://github.com/ggml-org/llama.cpp/security/advisories/GHSA-j8rj-fmpv-wcxw
- https://nvd.nist.gov/vuln/detail/CVE-2026-34159
- https://github.com/ggml-org/llama.cpp/commit/39bf0d3c6a95803e0f41aaba069ffbee26721042
- https://github.com/ggml-org/llama.cpp/pull/20908
