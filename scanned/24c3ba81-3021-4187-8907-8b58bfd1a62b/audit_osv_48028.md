# [M] CVE-2017-17449

## Summary
Severity: Medium
Advisory: CVE-2017-17449
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-12-07
Source: https://osv.dev/vulnerability/CVE-2017-17449
Type: osv

## Details
The __netlink_deliver_tap_skb function in net/netlink/af_netlink.c in the Linux kernel through 4.14.4, when CONFIG_NLMON is enabled, does not restrict observations of Netlink messages to a single net namespace, which allows local users to obtain sensitive information by leveraging the CAP_NET_ADMIN capability to sniff an nlmon interface for all Netlink activity on the system.

## References
- https://usn.ubuntu.com/3653-2/
- https://source.android.com/security/bulletin/pixel/2018-04-01
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3655-1/
- https://usn.ubuntu.com/3655-2/
- https://usn.ubuntu.com/3653-1/
- https://usn.ubuntu.com/3657-1/
- https://www.debian.org/security/2017/dsa-4073
- https://www.debian.org/security/2018/dsa-4082
- https://lkml.org/lkml/2017/12/5/950
- https://access.redhat.com/errata/RHSA-2018:1062
- https://access.redhat.com/errata/RHSA-2018:1170
- http://www.securityfocus.com/bid/102122
- https://access.redhat.com/errata/RHSA-2018:1130
- https://access.redhat.com/errata/RHSA-2018:0654
- https://access.redhat.com/errata/RHSA-2018:0676
