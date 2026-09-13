# [M] power: supply: bq27xxx-i2c: Do not free non existing IRQ

## Summary
Severity: Medium
Advisory: CVE-2024-27412
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-27412
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.309, >=4.20.0 <5.4.271, >=5.5.0 <5.10.212, >=5.11.0 <5.15.151, >=5.16.0 <6.1.81, >=6.2.0 <6.6.21, >=6.4.0 <6.7.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

power: supply: bq27xxx-i2c: Do not free non existing IRQ

The bq27xxx i2c-client may not have an IRQ, in which case
client->irq will be 0. bq27xxx_battery_i2c_probe() already has
an if (client->irq) check wrapping the request_threaded_irq().

But bq27xxx_battery_i2c_remove() unconditionally calls
free_irq(client->irq) leading to:

[  190.310742] ------------[ cut here ]------------
[  190.310843] Trying to free already-free IRQ 0
[  190.310861] WARNING: CPU: 2 PID: 1304 at kernel/irq/manage.c:1893 free_irq+0x1b8/0x310

Followed by a backtrace when unbinding the driver. Add
an if (client->irq) to bq27xxx_battery_i2c_remove() mirroring
probe() to fix this.

## References
- https://git.kernel.org/stable/c/083686474e7c97b0f8b66df37fcb64e432e8b771
- https://git.kernel.org/stable/c/2df70149e73e79783bcbc7db4fa51ecef0e2022c
- https://git.kernel.org/stable/c/7394abc8926adee6a817bab10797e0adc898af77
- https://git.kernel.org/stable/c/cefe18e9ec84f8fe3e198ccebb815cc996eb9797
- https://git.kernel.org/stable/c/d4d813c0a14d6bf52d810a55db06a2e7e3d98eaa
- https://git.kernel.org/stable/c/d7acc4a569f5f4513120c85ea2b9f04909b7490f
- https://git.kernel.org/stable/c/e601ae81910ce6a3797876e190a2d8ef6cf828bc
- https://git.kernel.org/stable/c/fbca8bae1ba79d443a58781b45e92a73a24ac8f8
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27412.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27412
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
