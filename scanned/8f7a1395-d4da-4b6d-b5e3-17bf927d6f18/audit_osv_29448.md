# [C] llama.cpp allows write-what-where in rpc_server::set_tensor

## Summary
Severity: Critical
Advisory: CVE-2024-42479
Aliases: GHSA-wcr5-566p-9cwj
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-08-12
Source: https://osv.dev/vulnerability/CVE-2024-42479
Type: osv

## Details
llama.cpp provides LLM inference in C/C++. The unsafe `data` pointer member in the `rpc_tensor` structure can cause arbitrary address writing. This vulnerability is fixed in b3561.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42479.json
- https://github.com/ggerganov/llama.cpp/security/advisories/GHSA-wcr5-566p-9cwj
- https://nvd.nist.gov/vuln/detail/CVE-2024-42479
- https://github.com/ggerganov/llama.cpp/commit/b72942fac998672a79a1ae3c03b340f7e629980b
