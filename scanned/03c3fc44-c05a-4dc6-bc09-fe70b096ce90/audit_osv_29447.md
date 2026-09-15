# [M] llama.cpp allows Arbitrary Address Read in rpc_server::get_tensor

## Summary
Severity: Medium
Advisory: CVE-2024-42478
Aliases: GHSA-5vm9-p64x-gqw9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-08-12
Source: https://osv.dev/vulnerability/CVE-2024-42478
Type: osv

## Details
llama.cpp provides LLM inference in C/C++. The unsafe `data` pointer member in the `rpc_tensor` structure can cause arbitrary address reading. This vulnerability is fixed in b3561.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42478.json
- https://github.com/ggerganov/llama.cpp/security/advisories/GHSA-5vm9-p64x-gqw9
- https://nvd.nist.gov/vuln/detail/CVE-2024-42478
- https://github.com/ggerganov/llama.cpp/commit/b72942fac998672a79a1ae3c03b340f7e629980b
