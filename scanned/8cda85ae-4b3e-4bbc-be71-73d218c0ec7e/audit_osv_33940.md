# [C] Integer Overflow or Wraparound vulnerability in dragonflydb/dragonfly

## Summary
Severity: Critical
Advisory: CVE-2025-52935
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/S:N/AU:Y/R:U/V:C/RE:M/U:Red)
Published: 2025-06-23
Source: https://osv.dev/vulnerability/CVE-2025-52935
Type: osv

## Details
Integer Overflow or Wraparound vulnerability in dragonflydb dragonfly (src/redis/lua/struct modules). This vulnerability is associated with program files lua_struct.C.

This issue affects dragonfly: 1.30.1, 1.30.0, 1.28.18.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52935.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-52935
- https://github.com/dragonflydb/dragonfly/commit/473e002c848eb312f23d84114eb4951a7c4af5a1
- https://github.com/dragonflydb/dragonfly/pull/4996
- https://github.com/dragonflydb/dragonfly
