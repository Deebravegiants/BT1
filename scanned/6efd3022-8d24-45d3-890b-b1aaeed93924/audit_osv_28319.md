# [H] OpenComputers Denial of Service using xpcall

## Summary
Severity: High
Advisory: CVE-2024-31446
Aliases: GHSA-54j4-xpgj-cq4g
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-31446
Type: osv

## Details
OpenComputers is a Minecraft mod that adds programmable computers and robots to the game. A user can use OpenComputers to get a Computer thread stuck in the Lua VM, which eventually blocks the Server thread, requiring the server to be forcibly shut down. This can be accomplished using any device in the mod and can be performed by anyone who can execute Lua code on them. This occurs while using the native Lua library. LuaJ appears to not have this issue. This vulnerability is fixed in 1.8.4. The GregTech: New Horizons modpack uses its own modified version of OpenComputers. They have applied the relevant patch in version 1.10.10-GTNH.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31446.json
- https://github.com/MightyPirates/OpenComputers/security/advisories/GHSA-54j4-xpgj-cq4g
- https://nvd.nist.gov/vuln/detail/CVE-2024-31446
- https://github.com/MightyPirates/OpenComputers/commit/9d4f7ea297953c2fd8ccfd24fe549d5e9576400f
