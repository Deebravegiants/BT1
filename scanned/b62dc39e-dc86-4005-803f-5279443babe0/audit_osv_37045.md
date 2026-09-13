# [H] llama.cpp has a Heap Buffer Overflow via Integer Overflow in `mem_size` Calculation — Bypass of CVE-2025-53630 Fix

## Summary
Severity: High
Advisory: CVE-2026-27940
Aliases: GHSA-3p4r-fq3f-q74v
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-12
Source: https://osv.dev/vulnerability/CVE-2026-27940
Type: osv

## Details
llama.cpp is an inference of several LLM models in C/C++. Prior to b8146, the gguf_init_from_file_impl() in gguf.cpp is vulnerable to an Integer overflow, leading to an undersized heap allocation. Using the subsequent fread() writes 528+ bytes of attacker-controlled data past the buffer boundary. This is a bypass of a similar bug in the same file - CVE-2025-53630, but the fix overlooked some areas. This vulnerability is fixed in b8146.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27940.json
- https://github.com/ggml-org/llama.cpp/security/advisories/GHSA-3p4r-fq3f-q74v
- https://nvd.nist.gov/vuln/detail/CVE-2026-27940
