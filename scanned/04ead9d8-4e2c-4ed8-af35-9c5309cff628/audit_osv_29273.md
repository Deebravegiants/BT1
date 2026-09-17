# [M] llama.cpp null pointer dereference in gguf_init_from_file

## Summary
Severity: Medium
Advisory: CVE-2024-41130
Aliases: GHSA-49q7-2jmh-92fp
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2024-07-22
Source: https://osv.dev/vulnerability/CVE-2024-41130
Type: osv

## Details
llama.cpp provides LLM inference in C/C++. Prior to b3427, llama.cpp contains a null pointer dereference in gguf_init_from_file. This vulnerability is fixed in b3427.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41130.json
- https://github.com/ggerganov/llama.cpp/security/advisories/GHSA-49q7-2jmh-92fp
- https://nvd.nist.gov/vuln/detail/CVE-2024-41130
- https://github.com/ggerganov/llama.cpp/commit/07283b1a90e1320aae4762c7e03c879043910252
