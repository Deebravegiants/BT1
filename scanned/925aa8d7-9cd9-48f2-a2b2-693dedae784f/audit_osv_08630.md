# [H] CVE-2016-4997

## Summary
Severity: High
Advisory: CVE-2016-4997
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-07-03
Source: https://osv.dev/vulnerability/CVE-2016-4997
Type: osv

## Details
The compat IPT_SO_SET_REPLACE and IP6T_SO_SET_REPLACE setsockopt implementations in the netfilter subsystem in the Linux kernel before 4.6.3 allow local users to gain privileges or cause a denial of service (memory corruption) by leveraging in-container root access to provide a crafted offset value that triggers an unintended decrement.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00027.html
- http://rhn.redhat.com/errata/RHSA-2016-1847.html
- http://rhn.redhat.com/errata/RHSA-2016-1883.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.6.3
- http://www.ubuntu.com/usn/USN-3016-2
- http://www.ubuntu.com/usn/USN-3018-1
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00048.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.securityfocus.com/bid/91451
- http://www.ubuntu.com/usn/USN-3017-2
- http://www.ubuntu.com/usn/USN-3019-1
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05347541
- https://www.exploit-db.com/exploits/40489/
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00060.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00051.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00007.html
- http://www.openwall.com/lists/oss-security/2016/06/24/5
- http://www.ubuntu.com/usn/USN-3020-1
- http://www.oracle.com/technetwork/topics/security/ovmbulletinoct2016-3090547.html
