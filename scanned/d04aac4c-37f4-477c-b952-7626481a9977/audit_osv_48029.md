# [H] CVE-2017-17450

## Summary
Severity: High
Advisory: CVE-2017-17450
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-07
Source: https://osv.dev/vulnerability/CVE-2017-17450
Type: osv

## Details
net/netfilter/xt_osf.c in the Linux kernel through 4.14.4 does not require the CAP_NET_ADMIN capability for add_callback and remove_callback operations, which allows local users to bypass intended access restrictions because the xt_osf_fingers data structure is shared across all net namespaces.

## References
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3632-1/
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00007.html
- https://usn.ubuntu.com/3583-2/
- https://usn.ubuntu.com/3617-1/
- https://usn.ubuntu.com/3617-2/
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3583-1/
- https://usn.ubuntu.com/3617-3/
- https://www.debian.org/security/2018/dsa-4082
- https://www.debian.org/security/2017/dsa-4073
- http://www.securityfocus.com/bid/102110
- https://lkml.org/lkml/2017/12/5/982
