# [H] CVE-2017-17448

## Summary
Severity: High
Advisory: CVE-2017-17448
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-07
Source: https://osv.dev/vulnerability/CVE-2017-17448
Type: osv

## Details
net/netfilter/nfnetlink_cthelper.c in the Linux kernel through 4.14.4 does not require the CAP_NET_ADMIN capability for new, get, and del operations, which allows local users to bypass intended access restrictions because the nfnl_cthelper_list data structure is shared across all net namespaces.

## References
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3620-1/
- https://usn.ubuntu.com/3632-1/
- https://usn.ubuntu.com/3617-1/
- https://usn.ubuntu.com/3617-3/
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3617-2/
- https://usn.ubuntu.com/3620-2/
- http://www.securityfocus.com/bid/102117
- https://www.debian.org/security/2018/dsa-4082
- https://access.redhat.com/errata/RHSA-2018:0654
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2018:1062
- https://www.debian.org/security/2017/dsa-4073
- https://patchwork.kernel.org/patch/10089373/
