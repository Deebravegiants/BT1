# [M] CVE-2020-35521

## Summary
Severity: Medium
Advisory: CVE-2020-35521
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-03-09
Source: https://osv.dev/vulnerability/CVE-2020-35521
Type: osv

## Details
A flaw was found in libtiff. Due to a memory allocation failure in tif_read.c, a crafted TIFF file can lead to an abort, resulting in denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BMHBYFMX3D5VGR6Y3RXTTH3Q4NF4E6IG/
- https://security.gentoo.org/glsa/202104-06
- https://security.netapp.com/advisory/ntap-20210521-0009/
- https://bugzilla.redhat.com/show_bug.cgi?id=1932034
