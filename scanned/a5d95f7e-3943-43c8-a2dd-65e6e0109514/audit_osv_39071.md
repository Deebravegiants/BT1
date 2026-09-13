# [C] llama.cpp b1886–b7445 Double Free via llama-android.cpp

## Summary
Severity: Critical
Advisory: CVE-2026-43622
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-43622
Type: osv

## Details
llama.cpp builds b1886 through b7445 contain a double free vulnerability in the LLaMA-Android JNI wrapper where new_1batch() allocates memory using malloc() while free_1batch() deallocates it using the C++ delete operator, causing heap metadata corruption. Attackers can trigger this memory management mismatch to cause denial of service through process crashes or potentially achieve arbitrary code execution depending on allocator state.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43622.json
- https://github.com/ggml-org/llama.cpp/releases/tag/b7446
- https://nvd.nist.gov/vuln/detail/CVE-2026-43622
- https://www.vulncheck.com/advisories/llama-cpp-b1886-b7445-double-free-via-llama-android-cpp
- https://github.com/ggml-org/llama.cpp/commit/5c0d18881e0e9794c96b2602736b758bac9d9388
- https://github.com/Vladimir-tokarev-cyera/llama-cpp-security-patches
