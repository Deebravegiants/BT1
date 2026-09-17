# [H] CVE-2018-1000026

## Summary
Severity: High
Advisory: CVE-2018-1000026
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2018-1000026
Type: osv

## Details
Linux Linux kernel version at least v4.8 onwards, probably well before contains a Insufficient input validation vulnerability in bnx2x network card driver that can result in DoS: Network card firmware assertion takes card off-line. This attack appear to be exploitable via An attacker on a must pass a very large, specially crafted packet to the bnx2x card. This can be done from an untrusted guest VM..

## References
- http://lists.openwall.net/netdev/2018/01/18/96
- https://lists.debian.org/debian-lts-announce/2019/05/msg00002.html
- https://usn.ubuntu.com/3619-1/
- http://lists.openwall.net/netdev/2018/01/16/40
- https://access.redhat.com/errata/RHSA-2018:3083
- https://access.redhat.com/errata/RHSA-2018:3096
- https://patchwork.ozlabs.org/patch/859410/
- https://usn.ubuntu.com/3617-1/
- https://usn.ubuntu.com/3620-2/
- https://access.redhat.com/errata/RHSA-2018:2948
- https://usn.ubuntu.com/3632-1/
- https://usn.ubuntu.com/3617-2/
- https://usn.ubuntu.com/3617-3/
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3620-1/
