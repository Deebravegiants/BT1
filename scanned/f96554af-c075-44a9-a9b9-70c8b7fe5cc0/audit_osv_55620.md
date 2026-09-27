# [H] llama.cpp has Out-of-bounds Write in llama-server

## Summary
Severity: High
Advisory: CVE-2026-21869
Aliases: GHSA-8947-pfff-2f3c
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21869
Type: osv

## Details
llama.cpp is an inference of several LLM models in C/C++. In commits 55d4206c8 and prior, the n_discard parameter is parsed directly from JSON input in the llama.cpp server's completion endpoints without validation to ensure it's non-negative. When a negative value is supplied and the context fills up, llama_memory_seq_rm/add receives a reversed range and negative offset, causing out-of-bounds memory writes in the token evaluation loop. This deterministic memory corruption can crash the process or enable remote code execution (RCE). There is no fix at the time of publication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21869.json
- https://github.com/ggml-org/llama.cpp/security/advisories/GHSA-8947-pfff-2f3c
- https://nvd.nist.gov/vuln/detail/CVE-2026-21869
