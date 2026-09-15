# [M] llama.cpp global-buffer-overflow in ggml_type_size

## Summary
Severity: Medium
Advisory: CVE-2024-42477
Aliases: GHSA-mqp6-7pv6-fqjf
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-08-12
Source: https://osv.dev/vulnerability/CVE-2024-42477
Type: osv

## Details
llama.cpp provides LLM inference in C/C++. The unsafe `type` member in the `rpc_tensor` structure can cause `global-buffer-overflow`. This vulnerability may lead to memory data leakage. The vulnerability is fixed in b3561.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42477.json
- https://github.com/ggerganov/llama.cpp/security/advisories/GHSA-mqp6-7pv6-fqjf
- https://nvd.nist.gov/vuln/detail/CVE-2024-42477
- https://github.com/ggerganov/llama.cpp/commit/b72942fac998672a79a1ae3c03b340f7e629980b
