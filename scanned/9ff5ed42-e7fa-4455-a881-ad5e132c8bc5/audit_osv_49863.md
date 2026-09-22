# [M] CVE-2019-20054

## Summary
Severity: Medium
Advisory: CVE-2019-20054
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-28
Source: https://osv.dev/vulnerability/CVE-2019-20054
Type: osv

## Details
In the Linux kernel before 5.0.6, there is a NULL pointer dereference in drop_sysctl_table() in fs/proc/proc_sysctl.c, related to put_links, aka CID-23da9588037e.

## References
- https://security.netapp.com/advisory/ntap-20200204-0002/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.11
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.6
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=89189557b47b35683a27c80ee78aef18248eefb4
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=23da9588037ecdd4901db76a5b79a42b529c4ec3
