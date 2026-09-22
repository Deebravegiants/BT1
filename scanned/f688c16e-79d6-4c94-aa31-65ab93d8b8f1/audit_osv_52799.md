# [H] CVE-2022-1350

## Summary
Severity: High
Advisory: CVE-2022-1350
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-04-14
Source: https://osv.dev/vulnerability/CVE-2022-1350
Type: osv

## Details
A vulnerability classified as problematic was found in GhostPCL 9.55.0. This vulnerability affects the function chunk_free_object of the file gsmchunk.c. The manipulation with a malicious file leads to a memory corruption. The attack can be initiated remotely but requires user interaction. The exploit has been disclosed to the public as a POC and may be used. It is recommended to apply the patches to fix this issue.

## References
- https://vuldb.com/?id.197290
- https://bugs.ghostscript.com/attachment.cgi?id=22323
- https://bugs.ghostscript.com/show_bug.cgi?id=705156
