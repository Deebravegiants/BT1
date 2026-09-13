# [H] hwmon: (pmbus/adm1266) cap PDIO scan in get_multiple at ADM1266_PDIO_NR

## Summary
Severity: High
Advisory: CVE-2026-64084
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64084
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (pmbus/adm1266) cap PDIO scan in get_multiple at ADM1266_PDIO_NR

adm1266_gpio_get_multiple() iterates the PDIO portion of the
caller-supplied mask using

	for_each_set_bit_from(gpio_nr, mask,
			      ADM1266_GPIO_NR + ADM1266_PDIO_STATUS) {
		...
	}

where ADM1266_PDIO_STATUS is the PMBus command code (0xE9, i.e. 233),
not the number of PDIO pins.  The intended upper bound is
ADM1266_GPIO_NR + ADM1266_PDIO_NR = 25.

gpiolib hands in a mask sized for gc.ngpio (= 25 bits on this chip),
so the iteration walks find_next_bit() up to 242, reading up to 217
extra bits (a handful of unsigned-long words: four on 64-bit, seven
on 32-bit) of whatever lives past the end of the mask in the
caller's stack.  Any incidental set bit in that range then drives a
set_bit(gpio_nr, bits) call that writes past the end of the
caller-supplied bits array too -- both out-of-bounds.

Substitute ADM1266_PDIO_NR for the constant so the scan stops at the
last real PDIO bit.

## References
- https://git.kernel.org/stable/c/17cee2f59029039416e8f6303050038eb59ba149
- https://git.kernel.org/stable/c/299efd14c2eda7e5fd40025e54addd4151a01081
- https://git.kernel.org/stable/c/2aef8f08c479f4cbc83e1e6b19d1c94d4dd24f17
- https://git.kernel.org/stable/c/4d1da9a6be5a8156c532d571c2ed237169f99244
- https://git.kernel.org/stable/c/b96c7f0bc0713dc6403912f6527d4ff9168d6fe6
- https://git.kernel.org/stable/c/d0593e15fdeb56048a72c5c6e720f702759d0ccd
- https://git.kernel.org/stable/c/d7834d92251baade796812876e95555e2066fa9f
- https://git.kernel.org/stable/c/fa7ca363069a70b0d1aa51e8892e3095fe2ac1ec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64084.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64084
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
