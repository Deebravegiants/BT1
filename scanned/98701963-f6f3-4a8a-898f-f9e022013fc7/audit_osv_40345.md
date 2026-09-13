# [H] netfilter: nat: use kfree_rcu to release ops

## Summary
Severity: High
Advisory: CVE-2026-53000
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53000
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nat: use kfree_rcu to release ops

Florian Westphal says:

"Historically this is not an issue, even for normal base hooks: the data
path doesn't use the original nf_hook_ops that are used to register the
callbacks.

However, in v5.14 I added the ability to dump the active netfilter
hooks from userspace.

This code will peek back into the nf_hook_ops that are available
at the tail of the pointer-array blob used by the datapath.

The nat hooks are special, because they are called indirectly from
the central nat dispatcher hook. They are currently invisible to
the nfnl hook dump subsystem though.

But once that changes the nat ops structures have to be deferred too."

Update nf_nat_register_fn() to deal with partial exposition of the hooks
from error path which can be also an issue for nfnetlink_hook.

## References
- https://git.kernel.org/stable/c/32fdd2e38e7435a368d88f5977a7d6585ebc8b0e
- https://git.kernel.org/stable/c/3c7511f38ab511b791196b13ae48bf4973bf7dfd
- https://git.kernel.org/stable/c/6eda0d771f94267f73f57c94630aa47e90957915
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53000.json
- https://access.redhat.com/errata/RHSA-2026:55445
- https://access.redhat.com/errata/RHSA-2026:64808
- https://access.redhat.com/security/cve/CVE-2026-53000
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53000.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53000
- https://bugzilla.redhat.com/show_bug.cgi?id=2492273
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
