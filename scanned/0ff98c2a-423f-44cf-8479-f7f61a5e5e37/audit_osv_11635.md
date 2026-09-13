# [M] CVE-2017-9147

## Summary
Severity: Medium
Advisory: CVE-2017-9147
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-22
Source: https://osv.dev/vulnerability/CVE-2017-9147
Type: osv

## Details
LibTIFF 4.0.7 has an invalid read in the _TIFFVGetField function in tif_dir.c, which might allow remote attackers to cause a denial of service (crash) via a crafted TIFF file.

## References
- http://www.securityfocus.com/bid/98594
- https://usn.ubuntu.com/3606-1/
- https://www.exploit-db.com/exploits/42301/
- http://www.debian.org/security/2017/dsa-3903
- http://bugzilla.maptools.org/show_bug.cgi?id=2693
