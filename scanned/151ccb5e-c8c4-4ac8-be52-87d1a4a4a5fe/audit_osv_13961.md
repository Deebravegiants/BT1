# [M] CVE-2018-5784

## Summary
Severity: Medium
Advisory: CVE-2018-5784
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-19
Source: https://osv.dev/vulnerability/CVE-2018-5784
Type: osv

## Details
In LibTIFF 4.0.9, there is an uncontrolled resource consumption in the TIFFSetDirectory function of tif_dir.c. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted tif file. This occurs because the declared number of directory entries is not validated against the actual number of directory entries.

## References
- https://lists.debian.org/debian-lts-announce/2018/05/msg00022.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00002.html
- https://usn.ubuntu.com/3602-1/
- https://usn.ubuntu.com/3606-1/
- https://www.debian.org/security/2018/dsa-4349
- http://bugzilla.maptools.org/show_bug.cgi?id=2772
- https://gitlab.com/libtiff/libtiff/commit/473851d211cf8805a161820337ca74cc9615d6ef
