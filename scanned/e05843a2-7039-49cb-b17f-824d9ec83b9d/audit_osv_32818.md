# [H] virtio: break and reset virtio devices on device_shutdown()

## Summary
Severity: High
Advisory: CVE-2025-38064
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38064
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <6.14.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio: break and reset virtio devices on device_shutdown()

Hongyu reported a hang on kexec in a VM. QEMU reported invalid memory
accesses during the hang.

	Invalid read at addr 0x102877002, size 2, region '(null)', reason: rejected
	Invalid write at addr 0x102877A44, size 2, region '(null)', reason: rejected
	...

It was traced down to virtio-console. Kexec works fine if virtio-console
is not in use.

The issue is that virtio-console continues to write to the MMIO even after
underlying virtio-pci device is reset.

Additionally, Eric noticed that IOMMUs are reset before devices, if
devices are not reset on shutdown they continue to poke at guest memory
and get errors from the IOMMU. Some devices get wedged then.

The problem can be solved by breaking all virtio devices on virtio
bus shutdown, then resetting them.

## References
- https://git.kernel.org/stable/c/8bd2fa086a04886798b505f28db4002525895203
- https://git.kernel.org/stable/c/aee42f3d57bfa37b2716df4584edeecf63b9df4c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38064.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38064
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
