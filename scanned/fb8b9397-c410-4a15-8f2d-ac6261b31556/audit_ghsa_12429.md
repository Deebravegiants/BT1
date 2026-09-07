# [C] memory overflow vulnerability in OpenEXR-viewer

## Summary
Severity: Critical
Advisory: GHSA-99jg-r3f4-rpxj
CVE: CVE-2023-50245
CWE: CWE-120
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-12
Source: https://github.com/advisories/GHSA-99jg-r3f4-rpxj
Type: github-advisory

## Affected
- GitHub Actions: `afichet/openexr-viewer` — affected >=0 <0.6.1

## Details
Just open this exr file through openexr-viewer.

( poc send by email )

This is windbg log file.

[ POC 2 ]
(8660.7e44): Access violation - code c0000005 (!!! second chance !!!)
openexr_viewer+0x27be4:
00007ff7`13ff7be4 c744880c0000803f mov     dword ptr [rax+rcx*4+0Ch],3F800000h ds:0000020a`3ac8000c=????????

Attempt to write the value 1.0 to the memory address 0x20A3AC8000C

[ POC 1 ]
(1404.9264): Access violation - code c0000005 (first chance)
First chance exceptions are reported before any exception handling.
This exception may be expected and handled.
openexr_viewer+0x27be4:
00007ff7`13ff7be4 c744880c0000803f mov     dword ptr [rax+rcx*4+0Ch],3F800000h ds:0000029c`b371600c=????????

Attempt to write the value 1.0 to the memory address 0x29CB371600C


Credits
Team : ZeroPointer
이동하 ( Lee Dong Ha of ZeroPointer Lab )
정지민    ( Jeong Jimin of ZeroPointer Lab )
박우진    ( Park Woojin of ZeroPointer Lab )
전우진    ( Jeon Woojin of ZeroPointer Lab )

## References
- https://github.com/afichet/openexr-viewer/security/advisories/GHSA-99jg-r3f4-rpxj
- https://nvd.nist.gov/vuln/detail/CVE-2023-50245
- https://github.com/afichet/openexr-viewer/commit/d0a7e85dfeb519951fb8a8d70f73f30d41cdd3d9
- https://github.com/afichet/openexr-viewer
