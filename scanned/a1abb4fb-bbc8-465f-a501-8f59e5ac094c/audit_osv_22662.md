# [H] Lua sandbox escape from mod in Minetest

## Summary
Severity: High
Advisory: CVE-2022-35978
Aliases: GHSA-663q-pcjw-27cc
CVSS: 7.7 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:H/A:L)
Published: 2022-08-15
Source: https://osv.dev/vulnerability/CVE-2022-35978
Type: osv

## Details
Minetest is a free open-source voxel game engine with easy modding and game creation. In **single player**, a mod can set a global setting that controls the Lua script loaded to display the main menu. The script is then loaded as soon as the game session is exited. The Lua environment the menu runs in is not sandboxed and can directly interfere with the user's system. There are currently no known workarounds.

## References
- https://dev.minetest.net/Changelog#5.5.0_.E2.86.92_5.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/35xxx/CVE-2022-35978.json
- https://github.com/minetest/minetest/security/advisories/GHSA-663q-pcjw-27cc
- https://nvd.nist.gov/vuln/detail/CVE-2022-35978
- https://github.com/minetest/minetest/commit/da71e86633d0b27cd02d7aac9fdac625d141ca13
