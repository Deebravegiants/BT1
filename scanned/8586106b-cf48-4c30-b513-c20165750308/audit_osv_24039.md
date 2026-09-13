# [H] net/smc: Fix possible leaked pernet namespace in smc_init()

## Summary
Severity: High
Advisory: CVE-2022-49905
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49905
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: Fix possible leaked pernet namespace in smc_init()

In smc_init(), register_pernet_subsys(&smc_net_stat_ops) is called
without any error handling.
If it fails, registering of &smc_net_ops won't be reverted.
And if smc_nl_init() fails, &smc_net_stat_ops itself won't be reverted.

This leaves wild ops in subsystem linkedlist and when another module
tries to call register_pernet_operations() it triggers page fault:

BUG: unable to handle page fault for address: fffffbfff81b964c
RIP: 0010:register_pernet_operations+0x1b9/0x5f0
Call Trace:
  <TASK>
  register_pernet_subsys+0x29/0x40
  ebtables_init+0x58/0x1000 [ebtables]
  ...

## References
- https://git.kernel.org/stable/c/61defd6450a9ef4a1487090449999b0fd83518ef
- https://git.kernel.org/stable/c/62ff373da2534534c55debe6c724c7fe14adb97f
- https://git.kernel.org/stable/c/c97daf836f7caf81d3144b8cd2b2a51f9bc3bd09
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49905.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49905
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
