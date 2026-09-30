# [M] CVE-2019-16234

## Summary
Severity: Medium
Advisory: CVE-2019-16234
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-11
Source: https://osv.dev/vulnerability/CVE-2019-16234
Type: osv

## Details
drivers/net/wireless/intel/iwlwifi/pcie/trans.c in the Linux kernel 5.2.14 does not check the alloc_workqueue return value, leading to a NULL pointer dereference.

## References
- https://usn.ubuntu.com/4342-1/
- https://usn.ubuntu.com/4346-1/
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://usn.ubuntu.com/4344-1/
- https://usn.ubuntu.com/4345-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00010.html
- https://lkml.org/lkml/2019/9/9/487
