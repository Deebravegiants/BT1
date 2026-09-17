# [C] llama.cpp b1886–b7445 Integer Overflow via new_1batch() in llama-android.cpp

## Summary
Severity: Critical
Advisory: CVE-2026-70638
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-70638
Type: osv

## Details
llama.cpp builds b1886 through b7445 contain an integer overflow vulnerability in the LLaMA-Android JNI wrapper where the new_1batch() function multiplies sizeof(llama_seq_id) by an attacker-controlled n_seq_max parameter without overflow validation, causing heap buffer allocation to wrap and allocate insufficient memory. Attackers can exploit this by providing a crafted n_seq_max value through a malicious model file or JNI call to trigger heap corruption and achieve denial of service or arbitrary code execution on Android applications using the LLaMA-Android binding.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70638.json
- https://github.com/ggml-org/llama.cpp/releases/tag/b7446
- https://nvd.nist.gov/vuln/detail/CVE-2026-70638
- https://www.vulncheck.com/advisories/llama-cpp-b1886-b7445-integer-overflow-via-new-1batch-in-llama-android-cpp
- https://github.com/ggml-org/llama.cpp/commit/5c0d18881e0e9794c96b2602736b758bac9d9388
- https://github.com/Vladimir-tokarev-cyera/llama-cpp-security-patches
