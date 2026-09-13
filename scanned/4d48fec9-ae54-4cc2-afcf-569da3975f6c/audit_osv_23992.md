# [M] scsi: scsi_transport_sas: Fix error handling in sas_phy_add()

## Summary
Severity: Medium
Advisory: CVE-2022-49839
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49839
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.14 <5.10.157, >=5.11.0 <5.15.80, >=5.16.0 <6.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: scsi_transport_sas: Fix error handling in sas_phy_add()

If transport_add_device() fails in sas_phy_add(), the kernel will crash
trying to delete the device in transport_remove_device() called from
sas_remove_host().

Unable to handle kernel NULL pointer dereference at virtual address 0000000000000108
CPU: 61 PID: 42829 Comm: rmmod Kdump: loaded Tainted: G        W          6.1.0-rc1+ #173
pstate: 60000005 (nZCv daif -PAN -UAO -TCO -DIT -SSBS BTYPE=--)
pc : device_del+0x54/0x3d0
lr : device_del+0x37c/0x3d0
Call trace:
 device_del+0x54/0x3d0
 attribute_container_class_device_del+0x28/0x38
 transport_remove_classdev+0x6c/0x80
 attribute_container_device_trigger+0x108/0x110
 transport_remove_device+0x28/0x38
 sas_phy_delete+0x30/0x60 [scsi_transport_sas]
 do_sas_phy_delete+0x6c/0x80 [scsi_transport_sas]
 device_for_each_child+0x68/0xb0
 sas_remove_children+0x40/0x50 [scsi_transport_sas]
 sas_remove_host+0x20/0x38 [scsi_transport_sas]
 hisi_sas_remove+0x40/0x68 [hisi_sas_main]
 hisi_sas_v2_remove+0x20/0x30 [hisi_sas_v2_hw]
 platform_remove+0x2c/0x60

Fix this by checking and handling return value of transport_add_device()
in sas_phy_add().

## References
- https://git.kernel.org/stable/c/03aabcb88aeeb7221ddb6196ae84ad5fb17b743f
- https://git.kernel.org/stable/c/2f21d653c648735657e23948b1d7ac7273de0f87
- https://git.kernel.org/stable/c/5d7bebf2dfb0dc97aac1fbace0910e557ecdb16f
- https://git.kernel.org/stable/c/c736876ee294bb4f271d76a25cc7d70c8537bc5d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49839.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49839
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
