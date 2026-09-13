# [H] CVE-2017-10688

## Summary
Severity: High
Advisory: CVE-2017-10688
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-29
Source: https://osv.dev/vulnerability/CVE-2017-10688
Type: osv

## Details
In LibTIFF 4.0.8, there is a assertion abort in the TIFFWriteDirectoryTagCheckedLong8Array function in tif_dirwrite.c. A crafted input will lead to a remote denial of service attack.

## References
- http://www.securityfocus.com/bid/99359
- https://usn.ubuntu.com/3602-1/
- https://www.exploit-db.com/exploits/42299/
- http://www.debian.org/security/2017/dsa-3903
- http://bugzilla.maptools.org/show_bug.cgi?id=2712
