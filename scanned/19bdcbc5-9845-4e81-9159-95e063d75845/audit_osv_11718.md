# [M] CVE-2017-9403

## Summary
Severity: Medium
Advisory: CVE-2017-9403
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9403
Type: osv

## Details
In LibTIFF 4.0.7, a memory leak vulnerability was found in the function TIFFReadDirEntryLong8Array in tif_dirread.c, which allows attackers to cause a denial of service via a crafted file.

## References
- http://www.debian.org/security/2017/dsa-3903
- https://security.gentoo.org/glsa/201709-27
- https://usn.ubuntu.com/3602-1/
- http://bugzilla.maptools.org/show_bug.cgi?id=2689
