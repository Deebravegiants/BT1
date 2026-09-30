# [H] CVE-2021-28927

## Summary
Severity: High
Advisory: CVE-2021-28927
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-07
Source: https://osv.dev/vulnerability/CVE-2021-28927
Type: osv

## Details
The text-to-speech engine in libretro RetroArch for Windows 1.9.0 passes unsanitized input to PowerShell through platform_win32.c via the accessibility_speak_windows function, which allows attackers who have write access on filesystems that are used by RetroArch to execute code via command injection using specially a crafted file and directory names.

## References
- https://github.com/libretro/RetroArch/blob/d3dc3ee989ec6a4903c689907ffc47027f71f776/frontend/drivers/platform_win32.c
- https://labs.bishopfox.com/advisories/retroarch-for-windows-version-1.9.0
