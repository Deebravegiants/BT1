# [H] netfilter: x_tables: add and use xtables_unregister_table_exit

## Summary
Severity: High
Advisory: CVE-2026-64078
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64078
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: x_tables: add and use xtables_unregister_table_exit

Previous change added xtables_unregister_table_pre_exit to detach the
table from the packetpath and to unlink it from the active table list.
In case of rmmod, userspace that is doing set/getsockopt for this table
will not be able to re-instantiate the table:
 1. The larval table has been removed already
 2. existing instantiated table is no longer on the xt pernet table list.

This adds the second stage helper:

unlink the table from the dying list, free the hook ops (if any) and do
the audit notification.  It replaces xt_unregister_table().

## References
- https://git.kernel.org/stable/c/8026e5163cca1d1db436c7bfb89ddea8b5e8c2cf
- https://git.kernel.org/stable/c/86ee5bc9c0f0e652e19f395675a432de11b75514
- https://git.kernel.org/stable/c/b4597d5fd7d2f8cebfffd40dffb5e003cc78964c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64078.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64078
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
