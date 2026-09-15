# [H] CVE-2024-25177

## Summary
Severity: High
Advisory: CVE-2024-25177
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-07
Source: https://osv.dev/vulnerability/CVE-2024-25177
Type: osv

## Details
LuaJIT through 2.1 and OpenRusty luajit2 before v2.1-20240314 have an unsinking of IR_FSTORE for NULL metatable, which leads to Denial of Service (DoS).

## References
- https://gist.github.com/pwnhacker0x18/a73f560d79f2c3d4011d6c5a2676f04a
- https://lists.debian.org/debian-lts-announce/2025/08/msg00022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25177.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25177
- https://github.com/LuaJIT/LuaJIT/issues/1147
- https://github.com/LuaJIT/LuaJIT/commit/85b4fed0b0353dd78c8c875c2f562d522a2b310f
- https://github.com/openresty/luajit2/commit/85b4fed0b0353dd78c8c875c2f562d522a2b310f
