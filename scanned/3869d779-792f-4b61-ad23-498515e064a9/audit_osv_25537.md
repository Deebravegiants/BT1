# [H] Deserialization of Untrusted Data in network IO

## Summary
Severity: High
Advisory: CVE-2023-38689
Aliases: GHSA-mcp7-xf3v-25x3
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-04
Source: https://osv.dev/vulnerability/CVE-2023-38689
Type: osv

## Details
Logistics Pipes is a modification (a.k.a. mod) for the computer game Minecraft Java Edition. The mod used Java's `ObjectInputStream#readObject` on untrusted data coming from clients or servers over the network resulting in possible remote code execution when sending specifically crafted network packets after connecting. The affected versions were released between 2013 and 2016 and the issue (back then unknown) was fixed in 2016 by a refactoring of the network IO code.  
The issue is present in all Logistics Pipes versions ranged from 0.7.0.91 prior to 0.10.0.71, which were downloaded from different platforms summing up to multi-million downloads. For Minecraft version 1.7.10 the issue was fixed in build 0.10.0.71. Everybody on Minecraft 1.7.10 should check their version number of Logistics Pipes in their modlist and update, if the version number is smaller than 0.10.0.71. Any newer supported Minecraft version (like 1.12.2) never had a Logistics Pipes version with vulnerable code. The best available workaround for vulnerable versions is to play in singleplayer only or update to newer Minecraft versions and modpacks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/38xxx/CVE-2023-38689.json
- https://github.com/RS485/LogisticsPipes/security/advisories/GHSA-mcp7-xf3v-25x3
- https://nvd.nist.gov/vuln/detail/CVE-2023-38689
- https://github.com/RS485/LogisticsPipes/commit/39a90b8f2d1a2bcc512ec68c3e139f1dac07aa56
- https://github.com/RS485/LogisticsPipes/commit/527c4f4fb028e9afab29d4e639935010ad7be9e7
