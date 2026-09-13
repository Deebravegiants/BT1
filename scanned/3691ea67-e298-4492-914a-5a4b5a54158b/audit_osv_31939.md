# [M] regulator: dummy: force synchronous probing

## Summary
Severity: Medium
Advisory: CVE-2025-22009
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-08
Source: https://osv.dev/vulnerability/CVE-2025-22009
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.85, >=6.7.0 <6.12.21, >=6.13.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

regulator: dummy: force synchronous probing

Sometimes I get a NULL pointer dereference at boot time in kobject_get()
with the following call stack:

anatop_regulator_probe()
 devm_regulator_register()
  regulator_register()
   regulator_resolve_supply()
    kobject_get()

By placing some extra BUG_ON() statements I could verify that this is
raised because probing of the 'dummy' regulator driver is not completed
('dummy_regulator_rdev' is still NULL).

In the JTAG debugger I can see that dummy_regulator_probe() and
anatop_regulator_probe() can be run by different kernel threads
(kworker/u4:*).  I haven't further investigated whether this can be
changed or if there are other possibilities to force synchronization
between these two probe routines.  On the other hand I don't expect much
boot time penalty by probing the 'dummy' regulator synchronously.

## References
- https://git.kernel.org/stable/c/5ade367b56c3947c990598df92395ce737bee872
- https://git.kernel.org/stable/c/8619909b38eeebd3e60910158d7d68441fc954e9
- https://git.kernel.org/stable/c/d3b83a1442a09b145006eb4294b1a963c5345c9c
- https://git.kernel.org/stable/c/e26f24ca4fb940b15e092796c5993142a2558bd9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22009.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22009
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
