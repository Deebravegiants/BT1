# [M] Insufficient input validation in efibootguard

## Summary
Severity: Medium
Advisory: CVE-2023-39950
Aliases: GHSA-j6pp-7g99-24m7
CVSS: 6.1 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:L)
Published: 2023-08-14
Source: https://osv.dev/vulnerability/CVE-2023-39950
Type: osv

## Details
efibootguard is a simple UEFI boot loader with support for safely switching between current and updated partition sets. Insufficient or missing validation and sanitization of input from untrustworthy bootloader environment files can cause crashes and probably also code injections into `bg_setenv`) or programs using `libebgenv`. This is triggered when the affected components try to modify a manipulated environment, in particular its user variables. Furthermore, `bg_printenv` may crash over invalid read accesses or report invalid results. Not affected by this issue is EFI Boot Guard's bootloader EFI binary. EFI Boot Guard release v0.15 contains required patches to sanitize and validate the bootloader environment prior to processing it in userspace. Its library and tools should be updated, so should programs statically linked against it. An update of the bootloader EFI executable is not required. The only way to prevent the issue with an unpatched EFI Boot Guard version is to avoid accesses to user variables, specifically modifications to them.

## References
- https://github.com/siemens/efibootguard/blob/master/docs/API.md
- https://github.com/siemens/efibootguard/blob/master/docs/TOOLS.md
- https://github.com/siemens/efibootguard/blob/master/docs/TOOLS.md#setting-user-variables
- https://github.com/siemens/efibootguard/tags
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39950.json
- https://github.com/siemens/efibootguard/security/advisories/GHSA-j6pp-7g99-24m7
- https://nvd.nist.gov/vuln/detail/CVE-2023-39950
