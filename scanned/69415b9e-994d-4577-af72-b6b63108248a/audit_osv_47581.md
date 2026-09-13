# [H] CVE-2016-8655

## Summary
Severity: High
Advisory: CVE-2016-8655
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-08
Source: https://osv.dev/vulnerability/CVE-2016-8655
Type: osv

## Details
Race condition in net/packet/af_packet.c in the Linux kernel through 4.8.12 allows local users to gain privileges or cause a denial of service (use-after-free) by leveraging the CAP_NET_RAW capability to change a socket version, related to the packet_set_ring and packet_setsockopt functions.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0387.html
- http://www.ubuntu.com/usn/USN-3151-2
- http://www.ubuntu.com/usn/USN-3151-4
- http://www.ubuntu.com/usn/USN-3151-3
- http://www.ubuntu.com/usn/USN-3149-2
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00087.html
- https://source.android.com/security/bulletin/2017-03-01.html
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00055.html
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00077.html
- http://www.openwall.com/lists/oss-security/2016/12/06/1
- http://www.securityfocus.com/bid/94692
- http://www.ubuntu.com/usn/USN-3149-1
- http://www.ubuntu.com/usn/USN-3152-1
- http://www.ubuntu.com/usn/USN-3152-2
- https://www.exploit-db.com/exploits/40871/
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00070.html
- http://rhn.redhat.com/errata/RHSA-2017-0386.html
- http://rhn.redhat.com/errata/RHSA-2017-0402.html
