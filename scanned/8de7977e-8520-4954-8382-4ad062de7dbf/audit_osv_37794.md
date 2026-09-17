# [H] llama.cpp has a Heap Buffer Overflow via Integer Overflow in GGUF Tensor Parsing

## Summary
Severity: High
Advisory: CVE-2026-33298
Aliases: GHSA-96jg-mvhq-q7q7
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/CVE-2026-33298
Type: osv

## Details
llama.cpp is an inference of several LLM models in C/C++. Prior to b7824, an integer overflow vulnerability in the `ggml_nbytes` function allows an attacker to bypass memory validation by crafting a GGUF file with specific tensor dimensions. This causes `ggml_nbytes` to return a significantly smaller size than required (e.g., 4MB instead of Exabytes), leading to a heap-based buffer overflow when the application subsequently processes the tensor. This vulnerability allows potential Remote Code Execution (RCE) via memory corruption. b7824 contains a fix.

## References
- https://github.com/ggml-org/llama.cpp/releases/tag/b7824
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33298.json
- https://github.com/ggml-org/llama.cpp/security/advisories/GHSA-96jg-mvhq-q7q7
- https://nvd.nist.gov/vuln/detail/CVE-2026-33298
