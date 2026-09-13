# [C] Luanti has a mod security sandbox escape

## Summary
Severity: Critical
Advisory: CVE-2026-41196
Aliases: CVE-2026-40959, GHSA-g596-mf82-w8c3
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-41196
Type: osv

## Details
Luanti (formerly Minetest) is an open source voxel game-creation platform. Starting in version 5.0.0 and prior to version 5.15.2, a malicious mod can trivially escape the sandboxed Lua environment to execute arbitrary code and gain full filesystem access on the user's device. This applies to the server-side mod, async and mapgen as well as the client-side (CSM) environments. This vulnerability is only exploitable when using LuaJIT. Version 5.15.2 contains a patch. On release versions, one can also patch this issue without recompiling by editing `builtin/init.lua` and adding the line `getfenv = nil` at the end. Note that this will break mods relying on this function (which is not inherently unsafe).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41196.json
- https://github.com/luanti-org/luanti/security/advisories/GHSA-g596-mf82-w8c3
- https://nvd.nist.gov/vuln/detail/CVE-2026-41196
- https://github.com/luanti-org/luanti/commit/8a929dfb97aa08337f49ba1bb96a56d6557dc896
