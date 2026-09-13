# [C] CVE-2024-25178

## Summary
Severity: Critical
Advisory: CVE-2024-25178
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-07-07
Source: https://osv.dev/vulnerability/CVE-2024-25178
Type: osv

## Details
LuaJIT through 2.1 and OpenRusty luajit2 before v2.1-20240314 have an out-of-bounds read in the stack-overflow handler in lj_state.c.

## References
- https://gist.github.com/pwnhacker0x18/423b4292f301ab274b42d5ed6e0b87d8
- https://lists.debian.org/debian-lts-announce/2025/08/msg00022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25178.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25178
- https://github.com/LuaJIT/LuaJIT/issues/1152
- https://github.com/LuaJIT/LuaJIT/commit/defe61a56751a0db5f00ff3ab7b8f45436ba74c8
- https://github.com/openresty/luajit2/commit/defe61a56751a0db5f00ff3ab7b8f45436ba74c8
