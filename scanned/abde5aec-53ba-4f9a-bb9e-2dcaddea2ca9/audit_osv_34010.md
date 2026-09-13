# [C] Integer Overflow in GGUF Parser can lead to Heap Out-of-Bounds Read/Write in gguf

## Summary
Severity: Critical
Advisory: CVE-2025-53630
Aliases: GHSA-vgg9-87g3-85w8
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-53630
Type: osv

## Details
llama.cpp is an inference of several LLM models in C/C++. Integer Overflow in the gguf_init_from_file_impl function in ggml/src/gguf.cpp can lead to Heap Out-of-Bounds Read/Write. This vulnerability is fixed in commit 26a48ad699d50b6268900062661bd22f3e792579.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53630.json
- https://github.com/ggml-org/llama.cpp/security/advisories/GHSA-vgg9-87g3-85w8
- https://nvd.nist.gov/vuln/detail/CVE-2025-53630
- https://github.com/ggml-org/llama.cpp/commit/26a48ad699d50b6268900062661bd22f3e792579
