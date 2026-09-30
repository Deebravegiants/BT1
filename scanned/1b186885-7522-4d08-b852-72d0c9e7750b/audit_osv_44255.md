# [H] i2c: amd-mp2: Unregister callback on adapter add failure

## Summary
Severity: High
Advisory: CVE-2026-80680
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80680
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: amd-mp2: Unregister callback on adapter add failure

amd_mp2_register_cb() stores the platform I2C context in the MP2 PCI
driver's callback table before the adapter is registered. If
i2c_add_adapter() fails, probe returns and devres frees the context,
but the PCI driver can still dereference the stale pointer from its IRQ
and system-sleep callbacks.

Unregister the callback before returning the adapter registration error.

## References
- https://git.kernel.org/stable/c/1883a09a37fed497b9efacf736c23624a472246b
- https://git.kernel.org/stable/c/2f7789b3a9628819ebf90bcba8f9da3c139f8687
- https://git.kernel.org/stable/c/4786d4d70dcd1e6b7e044f2348e00f201947b69c
- https://git.kernel.org/stable/c/82048795242f04275a3f49ffc66ad851b6120954
- https://git.kernel.org/stable/c/8bf719659406e4a1b56d441e0c7da2085d891d96
- https://git.kernel.org/stable/c/9142a3dcff0d80a3a24ce159aee19ddc869d9784
- https://git.kernel.org/stable/c/b7c2c5c8868737926410b93d1223ada17625ead3
- https://git.kernel.org/stable/c/cf107c5983dc70fcf932a305581a5f976d908ff1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80680.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80680
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
