# [C] Undefined Behavior Due to Out-of-Bounds Pointer Arithmetic in libwebsockets

## Summary
Severity: Critical
Advisory: CVE-2025-1866
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-03-03
Source: https://osv.dev/vulnerability/CVE-2025-1866
Type: osv

## Details
Improper Restriction of Operations within the Bounds of a Memory Buffer vulnerability in warmcat libwebsockets allows Pointer Manipulation, potentially leading to out-of-bounds memory access. This issue affects libwebsockets before 4.3.4 and is present in code built specifically for the Win32 platform.

By default, the affected code is not executed unless one of the following conditions is met:

LWS_WITHOUT_EXTENSIONS (default ON) is manually set to OFF in CMake.
LWS_WITH_HTTP_STREAM_COMPRESSION (default OFF) is manually set to ON in CMake.
Despite these conditions, when triggered in affected configurations, this vulnerability may allow attackers to manipulate pointers, potentially leading to memory corruption or unexpected behavior.

## References
- https://github.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1866.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1866
- https://github.com/warmcat/libwebsockets/commit/3f7c79fd57338aca1bf4a1b1f24e324b80d36265
