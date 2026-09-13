# [M] CVE-2019-16231

## Summary
Severity: Medium
Advisory: CVE-2019-16231
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-11
Source: https://osv.dev/vulnerability/CVE-2019-16231
Type: osv

## Details
drivers/net/fjes/fjes_main.c in the Linux kernel 5.2.14 does not check the alloc_workqueue return value, leading to a NULL pointer dereference.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00039.html
- https://usn.ubuntu.com/4227-1/
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://usn.ubuntu.com/4225-1/
- https://usn.ubuntu.com/4225-2/
- https://usn.ubuntu.com/4226-1/
- https://usn.ubuntu.com/4227-2/
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00035.html
- https://lkml.org/lkml/2019/9/9/487
