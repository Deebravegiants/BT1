# [H] CVE-2016-3627

## Summary
Severity: High
Advisory: CVE-2016-3627
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-17
Source: https://osv.dev/vulnerability/CVE-2016-3627
Type: osv

## Details
The xmlStringGetNodeList function in tree.c in libxml2 2.9.3 and earlier, when used in recovery mode, allows context-dependent attackers to cause a denial of service (infinite recursion, stack consumption, and application crash) via a crafted XML document.

## References
- https://kc.mcafee.com/corporate/index?page=content&id=SB10170
- http://rhn.redhat.com/errata/RHSA-2016-2957.html
- http://www.securityfocus.com/bid/84992
- http://www.securitytracker.com/id/1035335
- http://www.ubuntu.com/usn/USN-2994-1
- https://access.redhat.com/errata/RHSA-2016:1292
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05157239
- https://security.gentoo.org/glsa/201701-37
- https://www.tenable.com/security/tns-2016-18
- http://seclists.org/fulldisclosure/2016/May/10
- http://www.openwall.com/lists/oss-security/2016/03/21/2
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00055.html
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00127.html
- http://www.openwall.com/lists/oss-security/2016/03/21/3
- https://www.debian.org/security/2016/dsa-3593
