# [M] CVE-2020-21710

## Summary
Severity: Medium
Advisory: CVE-2020-21710
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-21710
Type: osv

## Details
A divide by zero issue discovered in eps_print_page in gdevepsn.c in Artifex Software GhostScript 9.50 allows remote attackers to cause a denial of service via opening of crafted PDF file.

## References
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=4e713293de84b689c4ab358f3e110ea54aa81925
- https://lists.debian.org/debian-lts-announce/2023/09/msg00029.html
- https://bugs.ghostscript.com/show_bug.cgi?id=701843
