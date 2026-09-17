# [H] opp: Fix use-after-free in lazy_opp_tables after probe deferral

## Summary
Severity: High
Advisory: CVE-2023-54026
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54026
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.121, >=5.16.0 <6.1.40, >=6.2.0 <6.4.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

opp: Fix use-after-free in lazy_opp_tables after probe deferral

When dev_pm_opp_of_find_icc_paths() in _allocate_opp_table() returns
-EPROBE_DEFER, the opp_table is freed again, to wait until all the
interconnect paths are available.

However, if the OPP table is using required-opps then it may already
have been added to the global lazy_opp_tables list. The error path
does not remove the opp_table from the list again.

This can cause crashes later when the provider of the required-opps
is added, since we will iterate over OPP tables that have already been
freed. E.g.:

  Unable to handle kernel NULL pointer dereference when read
  CPU: 0 PID: 7 Comm: kworker/0:0 Not tainted 6.4.0-rc3
  PC is at _of_add_opp_table_v2 (include/linux/of.h:949
  drivers/opp/of.c:98 drivers/opp/of.c:344 drivers/opp/of.c:404
  drivers/opp/of.c:1032) -> lazy_link_required_opp_table()

Fix this by calling _of_clear_opp_table() to remove the opp_table from
the list and clear other allocated resources. While at it, also add the
missing mutex_destroy() calls in the error path.

## References
- https://git.kernel.org/stable/c/39a0e723d3502f6dc4c603f57ebe8dc7bcc4a4bc
- https://git.kernel.org/stable/c/76ab057de777723ec924654502d1a260ba7d7d54
- https://git.kernel.org/stable/c/b2a2ab039bd58f51355e33d7d3fc64605d7f870d
- https://git.kernel.org/stable/c/c05e76d6b249e5254c31994eedd06dd3cc90dee0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54026.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54026
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
