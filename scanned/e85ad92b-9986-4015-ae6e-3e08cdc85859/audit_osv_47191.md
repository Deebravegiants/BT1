# [M] CVE-2016-10217

## Summary
Severity: Medium
Advisory: CVE-2016-10217
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-03
Source: https://osv.dev/vulnerability/CVE-2016-10217
Type: osv

## Details
The pdf14_open function in base/gdevp14.c in Artifex Software, Inc. Ghostscript 9.20 allows remote attackers to cause a denial of service (use-after-free and application crash) via a crafted file that is mishandled in the color management module.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=90fd0c7ca3efc1ddff64a86f4104b13b3ac969eb
- https://bugs.ghostscript.com/show_bug.cgi?id=697456
