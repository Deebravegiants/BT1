# [H] CVE-2019-19252

## Summary
Severity: High
Advisory: CVE-2019-19252
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-25
Source: https://osv.dev/vulnerability/CVE-2019-19252
Type: osv

## Details
vcs_write in drivers/tty/vt/vc_screen.c in the Linux kernel through 5.3.13 does not prevent write access to vcsu devices, aka CID-0c9acb1af77a.

## References
- https://usn.ubuntu.com/4284-1/
- https://lore.kernel.org/lkml/c30fc539-68a8-65d7-226c-6f8e6fd8bdfb%40suse.com/
- https://usn.ubuntu.com/4258-1/
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://git.kernel.org/pub/scm/linux/kernel/git/gregkh/tty.git/commit/?h=tty-testing&id=0c9acb1af77a3cb8707e43f45b72c95266903cee
