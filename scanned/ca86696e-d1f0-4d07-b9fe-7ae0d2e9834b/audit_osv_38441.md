# [C] MemProcFS < 5.17 DLL/Shared Library Hijacking

## Summary
Severity: Critical
Advisory: CVE-2026-40031
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-40031
Type: osv

## Details
MemProcFS before 5.17 contains multiple unsafe library-loading patterns that enable DLL and shared-library hijacking across six attack surfaces, including bare-name LoadLibraryU and dlopen calls without path qualification for vmmpyc, libMSCompression, and plugin DLLs. An attacker who places a malicious DLL or shared library in the working directory or manipulates LD_LIBRARY_PATH can achieve arbitrary code execution when MemProcFS loads.

## References
- https://github.com/ufrisk/MemProcFS/releases/tag/v5.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40031.json
- https://mobasi.ai/sentinel
- https://nvd.nist.gov/vuln/detail/CVE-2026-40031
- https://www.vulncheck.com/advisories/memprocfs-dll-shared-library-hijacking
- https://github.com/ufrisk/MemProcFS/commit/df80e6e83641f5004025ce661e6dd8139028d7b5
