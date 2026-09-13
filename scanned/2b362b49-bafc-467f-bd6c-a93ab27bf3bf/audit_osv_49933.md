# [H] CVE-2019-3900

## Summary
Severity: High
Advisory: CVE-2019-3900
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2019-04-25
Source: https://osv.dev/vulnerability/CVE-2019-3900
Type: osv

## Details
An infinite loop issue was found in the vhost_net kernel module in Linux Kernel up to and including v5.1-rc6, while handling incoming packets in handle_rx(). It could occur if one end sends packets faster than the other end can process them. A guest user, maybe remote one, could use this flaw to stall the vhost_net kernel thread, resulting in a DoS scenario.

## References
- https://access.redhat.com/errata/RHSA-2019:2043
- https://security.netapp.com/advisory/ntap-20190517-0005/
- https://usn.ubuntu.com/4118-1/
- https://access.redhat.com/errata/RHSA-2019:1973
- https://access.redhat.com/errata/RHSA-2019:3836
- https://seclists.org/bugtraq/2019/Aug/18
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://access.redhat.com/errata/RHSA-2019:3517
- https://access.redhat.com/errata/RHSA-2019:3967
- https://lists.debian.org/debian-lts-announce/2019/08/msg00017.html
- https://usn.ubuntu.com/4115-1/
- https://www.debian.org/security/2019/dsa-4497
- https://access.redhat.com/errata/RHSA-2019:2029
- https://lists.debian.org/debian-lts-announce/2019/08/msg00016.html
- https://usn.ubuntu.com/4116-1/
- https://access.redhat.com/errata/RHSA-2019:3309
- https://access.redhat.com/errata/RHSA-2020:0204
- https://usn.ubuntu.com/4114-1/
- https://access.redhat.com/errata/RHSA-2019:4058
- http://www.securityfocus.com/bid/108076
