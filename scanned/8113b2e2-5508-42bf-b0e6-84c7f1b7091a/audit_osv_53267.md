# [M] CVE-2022-3544

## Summary
Severity: Medium
Advisory: CVE-2022-3544
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-17
Source: https://osv.dev/vulnerability/CVE-2022-3544
Type: osv

## Details
A vulnerability, which was classified as problematic, was found in Linux Kernel. Affected is the function damon_sysfs_add_target of the file mm/damon/sysfs.c of the component Netfilter. The manipulation leads to memory leak. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-211044.

## References
- https://vuldb.com/?id.211044
- https://git.kernel.org/pub/scm/linux/kernel/git/netfilter/nf-next.git/commit/?id=1c8e2349f2d033f634d046063b704b2ca6c46972
