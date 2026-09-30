# [H] Use of Uninitialized Variable Vulnerability in llama.cpp

## Summary
Severity: High
Advisory: CVE-2024-32878
Aliases: GHSA-p5mv-gjc5-mwqv
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:L)
Published: 2024-04-26
Source: https://osv.dev/vulnerability/CVE-2024-32878
Type: osv

## Details
Llama.cpp is LLM inference in C/C++. There is a use of uninitialized heap variable vulnerability in gguf_init_from_file, the code will free this uninitialized variable later. In a simple POC, it will directly cause a crash. If the file is carefully constructed, it may be possible to control this uninitialized value and cause arbitrary address free problems. This may further lead to be exploited. Causes llama.cpp to crash (DoS) and may even lead to arbitrary code execution (RCE). This vulnerability has been patched in commit b2740.

## References
- https://github.com/ggerganov/llama.cpp/releases/tag/b2749
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32878.json
- https://github.com/ggerganov/llama.cpp/security/advisories/GHSA-p5mv-gjc5-mwqv
- https://nvd.nist.gov/vuln/detail/CVE-2024-32878
