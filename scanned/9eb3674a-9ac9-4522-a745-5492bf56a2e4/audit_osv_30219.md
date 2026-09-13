# [M] pinctrl: ocelot: fix system hang on level based interrupts

## Summary
Severity: Medium
Advisory: CVE-2024-50196
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50196
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.15.169, >=5.16.0 <6.1.114, >=6.2.0 <6.6.58, >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

pinctrl: ocelot: fix system hang on level based interrupts

The current implementation only calls chained_irq_enter() and
chained_irq_exit() if it detects pending interrupts.

```
for (i = 0; i < info->stride; i++) {
	uregmap_read(info->map, id_reg + 4 * i, &reg);
	if (!reg)
		continue;

	chained_irq_enter(parent_chip, desc);
```

However, in case of GPIO pin configured in level mode and the parent
controller configured in edge mode, GPIO interrupt might be lowered by the
hardware. In the result, if the interrupt is short enough, the parent
interrupt is still pending while the GPIO interrupt is cleared;
chained_irq_enter() never gets called and the system hangs trying to
service the parent interrupt.

Moving chained_irq_enter() and chained_irq_exit() outside the for loop
ensures that they are called even when GPIO interrupt is lowered by the
hardware.

The similar code with chained_irq_enter() / chained_irq_exit() functions
wrapping interrupt checking loop may be found in many other drivers:
```
grep -r -A 10 chained_irq_enter drivers/pinctrl
```

## References
- https://git.kernel.org/stable/c/20728e86289ab463b99b7ab4425515bd26aba417
- https://git.kernel.org/stable/c/4a81800ef05bea5a9896f199677f7b7f5020776a
- https://git.kernel.org/stable/c/655f5d4662b958122b260be05aa6dfdf8768efe6
- https://git.kernel.org/stable/c/93b8ddc54507a227087c60a0013ed833b6ae7d3c
- https://git.kernel.org/stable/c/dcbe9954634807ec54e22bde278b5b269f921381
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50196.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50196
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
