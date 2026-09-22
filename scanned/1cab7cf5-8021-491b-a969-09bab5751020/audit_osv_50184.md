# [H] CVE-2019-8912

## Summary
Severity: High
Advisory: CVE-2019-8912
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-18
Source: https://osv.dev/vulnerability/CVE-2019-8912
Type: osv

## Details
In the Linux kernel through 4.20.11, af_alg_release() in crypto/af_alg.c neglects to set a NULL value for a certain structure member, which leads to a use-after-free in sockfs_setattr.

## References
- https://access.redhat.com/errata/RHSA-2020:0174
- https://usn.ubuntu.com/3930-2/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00052.html
- http://www.securityfocus.com/bid/107063
- https://usn.ubuntu.com/3930-1/
- https://usn.ubuntu.com/3931-1/
- https://usn.ubuntu.com/3931-2/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-8912
- http://patchwork.ozlabs.org/patch/1042902/
