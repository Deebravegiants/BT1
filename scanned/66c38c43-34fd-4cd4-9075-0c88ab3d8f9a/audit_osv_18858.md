# [H] CVE-2020-36620

## Summary
Severity: High
Advisory: CVE-2020-36620
Aliases: GHSA-vq23-hwg7-hxrh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-21
Source: https://osv.dev/vulnerability/CVE-2020-36620
Type: osv

## Details
A vulnerability was found in Brondahl EnumStringValues up to 4.0.0. It has been declared as problematic. This vulnerability affects the function GetStringValuesWithPreferences_Uncache of the file EnumStringValues/EnumExtensions.cs. The manipulation leads to resource consumption. Upgrading to version 4.0.1 is able to address this issue. The name of the patch is c0fc7806beb24883cc2f9543ebc50c0820297307. It is recommended to upgrade the affected component. VDB-216466 is the identifier assigned to this vulnerability.

## References
- https://github.com/Brondahl/EnumStringValues/releases/tag/4.0.1
- https://vuldb.com/?id.216466
- https://github.com/Brondahl/EnumStringValues/commit/c0fc7806beb24883cc2f9543ebc50c0820297307
