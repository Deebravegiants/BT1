# [C] CVE-2015-7554

## Summary
Severity: Critical
Advisory: CVE-2015-7554
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-01-08
Source: https://osv.dev/vulnerability/CVE-2015-7554
Type: osv

## Details
The _TIFFVGetField function in tif_dir.c in libtiff 4.0.6 allows attackers to cause a denial of service (invalid memory write and crash) or possibly have unspecified other impact via crafted field data in an extension tag in a TIFF image.

## References
- http://rhn.redhat.com/errata/RHSA-2016-1546.html
- http://rhn.redhat.com/errata/RHSA-2016-1547.html
- https://security.gentoo.org/glsa/201701-16
- http://packetstormsecurity.com/files/135078/libtiff-4.0.6-Invalid-Write.html
- http://seclists.org/fulldisclosure/2015/Dec/119
- http://www.openwall.com/lists/oss-security/2015/12/26/7
- http://lists.opensuse.org/opensuse-updates/2016-01/msg00078.html
- http://lists.opensuse.org/opensuse-updates/2016-01/msg00081.html
- http://lists.opensuse.org/opensuse-updates/2016-01/msg00100.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://www.securityfocus.com/archive/1/537205/100/0/threaded
- http://www.securityfocus.com/bid/79699
