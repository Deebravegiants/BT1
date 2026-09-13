# [H] vfio/cdx: Serialize VFIO_DEVICE_SET_IRQS with a per-device mutex

## Summary
Severity: High
Advisory: CVE-2026-46036
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46036
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

vfio/cdx: Serialize VFIO_DEVICE_SET_IRQS with a per-device mutex

vfio_cdx_set_msi_trigger() reads vdev->config_msi and operates on the
vdev->cdx_irqs array based on its value, but provides no serialization
against concurrent VFIO_DEVICE_SET_IRQS ioctls.  Two callers can race
such that one observes config_msi as set while another clears it and
frees cdx_irqs via vfio_cdx_msi_disable(), resulting in a use-after-free
of the cdx_irqs array.

Add a cdx_irqs_lock mutex to struct vfio_cdx_device and acquire it in
vfio_cdx_set_msi_trigger(), which is the single chokepoint through
which all updates to config_msi, cdx_irqs, and msi_count flow, covering
both the ioctl path and the close-device cleanup path.  This keeps the
test of config_msi atomic with the subsequent enable, disable, or
trigger operations.

Drop the pre-call !cdx_irqs test from vfio_cdx_irqs_cleanup() as part
of this change: the optimization it provided is redundant with the
!config_msi early-return inside vfio_cdx_msi_disable(), and leaving the
test in place would be an unsynchronized read of state the new lock is
meant to protect.

## References
- https://git.kernel.org/stable/c/670e8864b1a218d72f08db40d0103adf38fa1d9b
- https://git.kernel.org/stable/c/7530f34ec0ca1438d45a75dcb43183a1cc92eced
- https://git.kernel.org/stable/c/7b436ade16cc81095d79b79f8efa3af0a4f5c5a2
- https://git.kernel.org/stable/c/ddf96e23c366c566283fce8377928851fa7f5e81
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46036.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46036
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
