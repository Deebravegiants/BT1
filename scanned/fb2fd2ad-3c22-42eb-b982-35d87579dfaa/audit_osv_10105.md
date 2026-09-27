# [M] CVE-2017-13727

## Summary
Severity: Medium
Advisory: CVE-2017-13727
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13727
Type: osv

## Details
There is a reachable assertion abort in the function TIFFWriteDirectoryTagSubifd() in LibTIFF 4.0.8, related to tif_dirwrite.c and a SubIFD tag. A crafted input will lead to a remote denial of service attack.

## References
- http://www.securityfocus.com/bid/100524
- https://usn.ubuntu.com/3602-1/
- https://www.debian.org/security/2018/dsa-4100
- http://bugzilla.maptools.org/show_bug.cgi?id=2728
