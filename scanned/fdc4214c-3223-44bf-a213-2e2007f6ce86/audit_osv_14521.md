# [M] CVE-2019-1010065

## Summary
Severity: Medium
Advisory: CVE-2019-1010065
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-18
Source: https://osv.dev/vulnerability/CVE-2019-1010065
Type: osv

## Details
The Sleuth Kit 4.6.0 and earlier is affected by: Integer Overflow. The impact is: Opening crafted disk image triggers crash in tsk/fs/hfs_dent.c:237. The component is: Overflow in fls tool used on HFS image. Bug is in tsk/fs/hfs.c file in function hfs_cat_traverse() in lines: 952, 1062. The attack vector is: Victim must open a crafted HFS filesystem image.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6VXDAP6SEO3RCDCZITTFGNZGSVPE5CTY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FGWCQIZKTDCJO4YGL5LGPYFNOVU7SJRX/
- https://lists.debian.org/debian-lts-announce/2022/06/msg00015.html
- https://issuetracker.google.com/issues/77809383
- https://github.com/sleuthkit/sleuthkit/commit/114cd3d0aac8bd1aeaf4b33840feb0163d342d5b
