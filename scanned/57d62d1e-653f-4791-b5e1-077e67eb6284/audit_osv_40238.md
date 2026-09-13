# [H] CVE-2026-52132

## Summary
Severity: High
Advisory: CVE-2026-52132
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-52132
Type: osv

## Details
llama.cpp through commit 97f06e9, when started with the --reranking flag, allows remote attackers to cause a denial of service (std::bad_alloc and HTTP 500) via a negative top_n value in a POST request to /rerank.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52132.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52132
- https://github.com/ggml-org/llama.cpp
- https://blog.ph4nt0m.xyz/ko/cves/cve-2026-52132/
