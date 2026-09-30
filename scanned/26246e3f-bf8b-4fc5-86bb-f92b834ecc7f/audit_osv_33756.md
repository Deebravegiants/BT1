# [H] llama.cpp Vulnerable to Buffer Overflow via Malicious GGUF Model

## Summary
Severity: High
Advisory: CVE-2025-49847
Aliases: GHSA-8wwf-w4qm-gpqr
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-06-17
Source: https://osv.dev/vulnerability/CVE-2025-49847
Type: osv

## Details
llama.cpp is an inference of several LLM models in C/C++. Prior to version b5662, an attacker‐supplied GGUF model vocabulary can trigger a buffer overflow in llama.cpp’s vocabulary‐loading code. Specifically, the helper _try_copy in llama.cpp/src/vocab.cpp: llama_vocab::impl::token_to_piece() casts a very large size_t token length into an int32_t, causing the length check (if (length < (int32_t)size)) to be bypassed. As a result, memcpy is still called with that oversized size, letting a malicious model overwrite memory beyond the intended buffer. This can lead to arbitrary memory corruption and potential code execution. This issue has been patched in version b5662.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49847.json
- https://github.com/ggml-org/llama.cpp/security/advisories/GHSA-8wwf-w4qm-gpqr
- https://nvd.nist.gov/vuln/detail/CVE-2025-49847
- https://github.com/ggml-org/llama.cpp/commit/3cfbbdb44e08fd19429fed6cc85b982a91f0efd5
