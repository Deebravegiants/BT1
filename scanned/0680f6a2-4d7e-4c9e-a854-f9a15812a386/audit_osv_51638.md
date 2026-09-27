# [M] CVE-2021-37220

## Summary
Severity: Medium
Advisory: CVE-2021-37220
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-07-21
Source: https://osv.dev/vulnerability/CVE-2021-37220
Type: osv

## Details
MuPDF through 1.18.1 has an out-of-bounds write because the cached color converter does not properly consider the maximum key size of a hash table. This can, for example, be seen with crafted "mutool draw" input.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TKRMREIYUBGG2GV73CU7BJNW2Q34IP23/
- http://git.ghostscript.com/?p=mupdf.git%3Bh=f5712c9949d026e4b891b25837edd2edc166151f
- https://bugs.ghostscript.com/show_bug.cgi?id=703791
