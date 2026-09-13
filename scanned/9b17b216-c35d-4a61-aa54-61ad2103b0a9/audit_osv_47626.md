# [C] CVE-2016-9555

## Summary
Severity: Critical
Advisory: CVE-2016-9555
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-11-28
Source: https://osv.dev/vulnerability/CVE-2016-9555
Type: osv

## Details
The sctp_sf_ootb function in net/sctp/sm_statefuns.c in the Linux kernel before 4.8.8 lacks chunk-length checking for the first chunk, which allows remote attackers to cause a denial of service (out-of-bounds slab access) or possibly have unspecified other impact via crafted SCTP data.

## References
- https://groups.google.com/forum/#%21topic/syzkaller/pAUcHsUJbjk
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00076.html
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00087.html
- http://rhn.redhat.com/errata/RHSA-2017-0086.html
- http://www.securitytracker.com/id/1037339
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00070.html
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00073.html
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00077.html
- http://rhn.redhat.com/errata/RHSA-2017-0113.html
- http://www.openwall.com/lists/oss-security/2016/11/22/18
- http://www.securityfocus.com/bid/94479
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00054.html
- https://bto.bluecoat.com/security-advisory/sa134
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00056.html
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00067.html
- http://rhn.redhat.com/errata/RHSA-2017-0091.html
- http://rhn.redhat.com/errata/RHSA-2017-0307.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.8
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00055.html
