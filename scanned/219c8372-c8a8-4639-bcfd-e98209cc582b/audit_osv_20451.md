# [C] CVE-2021-33806

## Summary
Severity: Critical
Advisory: CVE-2021-33806
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-03
Source: https://osv.dev/vulnerability/CVE-2021-33806
Type: osv

## Details
The BDew BdLib library before 1.16.1.7 for Minecraft allows remote code execution because it deserializes untrusted data in ObjectInputStream.readObject as part of its use of Java serialization.

## References
- https://bdew.net
- https://vuln.ryotak.me/advisories/46
- https://www.curseforge.com/minecraft/mc-mods/bdlib/files/3331330
- https://github.com/bdew-minecraft/bdlib/commit/447210530ceec72fb3374efecb0930ed359d2297
