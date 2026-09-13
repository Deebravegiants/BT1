# [M] CVE-2017-9936

## Summary
Severity: Medium
Advisory: CVE-2017-9936
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-26
Source: https://osv.dev/vulnerability/CVE-2017-9936
Type: osv

## Details
In LibTIFF 4.0.8, there is a memory leak in tif_jbig.c. A crafted TIFF document can lead to a memory leak resulting in a remote denial of service attack.

## References
- http://www.debian.org/security/2017/dsa-3903
- http://www.securityfocus.com/bid/99300
- https://usn.ubuntu.com/3602-1/
- http://bugzilla.maptools.org/show_bug.cgi?id=2706
- https://www.exploit-db.com/exploits/42300/
