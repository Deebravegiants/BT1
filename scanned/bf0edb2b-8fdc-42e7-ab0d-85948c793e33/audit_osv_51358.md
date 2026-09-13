# [M] CVE-2021-29650

## Summary
Severity: Medium
Advisory: CVE-2021-29650
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-30
Source: https://osv.dev/vulnerability/CVE-2021-29650
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.11.11. The netfilter subsystem allows attackers to cause a denial of service (panic) because net/netfilter/x_tables.c and include/linux/netfilter/x_tables.h lack a full memory barrier upon the assignment of a new table value, aka CID-175e476b8cdf.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RZGMUP6QEHJJEKPMLKOSPWYMW7PXFC2M/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VTADK5ELGTATGW2RK3K5MBJ2WGYCPZCM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WKRNELXLVFDY6Y5XDMWLIH3VKIMQXLLR/
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.11
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=175e476b8cdf2a4de7432583b49c871345e4f8a1
