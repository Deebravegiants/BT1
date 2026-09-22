# [M] Microsoft DirectX: .spritefont multiply overflow only in 32-bit builds

## Summary
Severity: Medium
Advisory: GHSA-c55g-rp4x-fx84
CWE: CWE-190
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-c55g-rp4x-fx84
Type: github-advisory

## Affected
- NuGet: `directxtk_desktop_win10` — affected >=0 <2026.5.8.1
- NuGet: `directxtk_uwp` — affected >=0 <2026.5.8.1

## Details
### Impact
The spritefont reader can be induced to perform a 32-bit overflow multiply that could in theory result in a RCE.

This impacts the use of the *DirectX Tool Kit* **SpriteFont** class file loading ctor if given untrusted data files.

> Note this only applies to x86/ARM builds of the library. ARM64 and x64 native is not subject to this issue.

### Patches
This bug has been fixed in the May 7, 2026 release. Alternatively, users can update their copy of the reader as per [this commit](https://github.com/microsoft/DirectXTK/commit/ef1bd5d7f492c39dd0cd87493ba8ea38725c9791).

### Workarounds
This does not apply if a project's .spritefont files are all 'trusted' data that were included with an application. It's primarily an issue only if developers are using user-provided or network downloaded spritefont files.

## References
- https://github.com/microsoft/DirectXTK/security/advisories/GHSA-c55g-rp4x-fx84
- https://github.com/microsoft/DirectXTK/commit/ef1bd5d7f492c39dd0cd87493ba8ea38725c9791
- https://github.com/microsoft/DirectXTK
- https://github.com/microsoft/DirectXTK/releases/tag/may2026
