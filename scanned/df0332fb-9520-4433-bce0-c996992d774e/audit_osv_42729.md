# [M] llama.cpp b1886–b7445 Null Pointer Dereference DoS via llama-android.cpp

## Summary
Severity: Medium
Advisory: CVE-2026-70639
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-70639
Type: osv

## Details
llama.cpp builds b1886 through b7445 contain a null pointer dereference vulnerability in the LLaMA-Android JNI wrapper where the bench_1model() function fails to validate the model context pointer before dereferencing it. Attackers can supply a malicious, corrupt, or truncated model file to trigger a null context condition, causing a SIGSEGV crash that terminates the Android application process and results in denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70639.json
- https://github.com/ggml-org/llama.cpp/releases/tag/b7446
- https://nvd.nist.gov/vuln/detail/CVE-2026-70639
- https://www.vulncheck.com/advisories/llama-cpp-b1886-b7445-null-pointer-dereference-dos-via-llama-android-cpp
- https://github.com/ggml-org/llama.cpp/commit/5c0d18881e0e9794c96b2602736b758bac9d9388
- https://github.com/Vladimir-tokarev-cyera/llama-cpp-security-patches
