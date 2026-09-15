# [H] mips: sched: Fix CPUMASK_OFFSTACK memory corruption

## Summary
Severity: High
Advisory: CVE-2026-72181
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72181
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.23 <5.10.265, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mips: sched: Fix CPUMASK_OFFSTACK memory corruption

This patch addresses a critical memory management flaw. When
CONFIG_CPUMASK_OFFSTACK is enabled, cpumask_var_t is a pointer.
Consequently, sizeof(new_mask) evaluates to the pointer size, causing
copy_from_user() to clobber the mask pointer. Furthermore, the old
logic performed copy_from_user() before allocating the mask.

Fix this by allocating new_mask first. To handle variable-sized user
masks correctly, use cpumask_size() to truncate overly large user masks
or pad undersized masks with zeros before copying the data directly into
the allocated buffer.

## References
- https://git.kernel.org/stable/c/15ba8053fe4162c933855f1676fb321cdb6251c7
- https://git.kernel.org/stable/c/1caee6e084a96ada94658f261ced377d85af3f03
- https://git.kernel.org/stable/c/2f7730c03a9deea3ba7a1c980070d363b4ea2046
- https://git.kernel.org/stable/c/3446ffb5d03c36f9ce88ede7ca5be319a2968d96
- https://git.kernel.org/stable/c/87a56c1e8e36d06ebe8640432f911538ded7827d
- https://git.kernel.org/stable/c/98e37db4a34d3af3fb2f4648295c25b5e40b20e3
- https://git.kernel.org/stable/c/a1dd41d00c57efb1fbc6f361c5f48c9d00cca51c
- https://git.kernel.org/stable/c/d20ee42f8226607b5693b2bc2f115ca2d270221a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72181.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72181
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
