# [H] llama.cpp tokenizer signed vs. unsigned heap overflow

## Summary
Severity: High
Advisory: CVE-2025-52566
Aliases: GHSA-7rxv-5jhh-j6xx
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-06-24
Source: https://osv.dev/vulnerability/CVE-2025-52566
Type: osv

## Details
llama.cpp is an inference of several LLM models in C/C++. Prior to version b5721, there is a signed vs. unsigned integer overflow in llama.cpp's tokenizer implementation (llama_vocab::tokenize) (src/llama-vocab.cpp:3036) resulting in unintended behavior in tokens copying size comparison. Allowing heap-overflowing llama.cpp inferencing engine with carefully manipulated text input during tokenization process. This issue has been patched in version b5721.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52566.json
- https://github.com/ggml-org/llama.cpp/security/advisories/GHSA-7rxv-5jhh-j6xx
- https://nvd.nist.gov/vuln/detail/CVE-2025-52566
- https://github.com/ggml-org/llama.cpp/commit/dd6e6d0b6a4bbe3ebfc931d1eb14db2f2b1d70af
