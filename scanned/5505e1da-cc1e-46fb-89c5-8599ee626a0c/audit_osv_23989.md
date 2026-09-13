# [H] ata: libata-transport: fix double ata_host_put() in ata_tport_add()

## Summary
Severity: High
Advisory: CVE-2022-49826
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49826
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <4.19.267, >=4.20.0 <5.4.225, >=5.5.0 <5.10.156, >=5.11.0 <5.15.80, >=5.16.0 <6.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ata: libata-transport: fix double ata_host_put() in ata_tport_add()

In the error path in ata_tport_add(), when calling put_device(),
ata_tport_release() is called, it will put the refcount of 'ap->host'.

And then ata_host_put() is called again, the refcount is decreased
to 0, ata_host_release() is called, all ports are freed and set to
null.

When unbinding the device after failure, ata_host_stop() is called
to release the resources, it leads a null-ptr-deref(), because all
the ports all freed and null.

Unable to handle kernel NULL pointer dereference at virtual address 0000000000000008
CPU: 7 PID: 18671 Comm: modprobe Kdump: loaded Tainted: G            E      6.1.0-rc3+ #8
pstate: 80400009 (Nzcv daif +PAN -UAO -TCO -DIT -SSBS BTYPE=--)
pc : ata_host_stop+0x3c/0x84 [libata]
lr : release_nodes+0x64/0xd0
Call trace:
 ata_host_stop+0x3c/0x84 [libata]
 release_nodes+0x64/0xd0
 devres_release_all+0xbc/0x1b0
 device_unbind_cleanup+0x20/0x70
 really_probe+0x158/0x320
 __driver_probe_device+0x84/0x120
 driver_probe_device+0x44/0x120
 __driver_attach+0xb4/0x220
 bus_for_each_dev+0x78/0xdc
 driver_attach+0x2c/0x40
 bus_add_driver+0x184/0x240
 driver_register+0x80/0x13c
 __pci_register_driver+0x4c/0x60
 ahci_pci_driver_init+0x30/0x1000 [ahci]

Fix this by removing redundant ata_host_put() in the error path.

## References
- https://git.kernel.org/stable/c/30e12e2be27ac6c4be2af4163c70db381364706f
- https://git.kernel.org/stable/c/377ff82c33c0cb74562a353361b64b33c09562cf
- https://git.kernel.org/stable/c/865a6da40ba092c18292ae5f6194756131293745
- https://git.kernel.org/stable/c/8c76310740807ade5ecdab5888f70ecb6d35732e
- https://git.kernel.org/stable/c/ac471468f7c16cda2525909946ca13ddbcd14000
- https://git.kernel.org/stable/c/bec9ded5404cb14e5f5470103d0973a2ff83d6a5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49826.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49826
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
