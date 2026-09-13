# [M] CVE-2019-10638

## Summary
Severity: Medium
Advisory: CVE-2019-10638
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2019-07-05
Source: https://osv.dev/vulnerability/CVE-2019-10638
Type: osv

## Details
In the Linux kernel before 5.1.7, a device can be tracked by an attacker using the IP ID values the kernel produces for connection-less protocols (e.g., UDP and ICMP). When such traffic is sent to multiple destination IP addresses, it is possible to obtain hash collisions (of indices to the counter array) and thereby obtain the hashing key (via enumeration). An attack may be conducted by hosting a crafted web page that uses WebRTC or gQUIC to force UDP traffic to attacker-controlled IP addresses.

## References
- https://usn.ubuntu.com/4118-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00014.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00016.html
- https://seclists.org/bugtraq/2019/Aug/13
- https://usn.ubuntu.com/4115-1/
- https://usn.ubuntu.com/4117-1/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00025.html
- https://seclists.org/bugtraq/2019/Aug/18
- https://seclists.org/bugtraq/2019/Nov/11
- http://packetstormsecurity.com/files/155212/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00017.html
- https://usn.ubuntu.com/4114-1/
- https://usn.ubuntu.com/4116-1/
- https://access.redhat.com/errata/RHSA-2019:3309
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.7
- https://www.debian.org/security/2019/dsa-4495
- http://www.securityfocus.com/bid/109092
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.8
- https://www.debian.org/security/2019/dsa-4497
