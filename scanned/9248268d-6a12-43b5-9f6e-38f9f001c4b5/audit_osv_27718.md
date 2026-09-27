# [C] CVE-2024-25176

## Summary
Severity: Critical
Advisory: CVE-2024-25176
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-07
Source: https://osv.dev/vulnerability/CVE-2024-25176
Type: osv

## Details
LuaJIT through 2.1 and OpenRusty luajit2 before v2.1-20240626 have a stack-buffer-overflow in lj_strfmt_wfnum in lj_strfmt_num.c.

## References
- https://gist.github.com/pwnhacker0x18/cd75d01fc7c9b6c85c183fbe5353d276
- https://lists.debian.org/debian-lts-announce/2025/08/msg00022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25176.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25176
- https://github.com/LuaJIT/LuaJIT/issues/1149
- https://github.com/LuaJIT/LuaJIT/commit/343ce0edaf3906a62022936175b2f5410024cbfc
- https://github.com/openresty/luajit2/commit/343ce0edaf3906a62022936175b2f5410024cbfc
