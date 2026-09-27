# [H] CVE-2021-47549

## Summary
Severity: High
Advisory: CVE-2021-47549
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47549
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

sata_fsl: fix UAF in sata_fsl_port_stop when rmmod sata_fsl

When the `rmmod sata_fsl.ko` command is executed in the PPC64 GNU/Linux,
a bug is reported:
 ==================================================================
 BUG: Unable to handle kernel data access on read at 0x80000800805b502c
 Oops: Kernel access of bad area, sig: 11 [#1]
 NIP [c0000000000388a4] .ioread32+0x4/0x20
 LR [80000000000c6034] .sata_fsl_port_stop+0x44/0xe0 [sata_fsl]
 Call Trace:
  .free_irq+0x1c/0x4e0 (unreliable)
  .ata_host_stop+0x74/0xd0 [libata]
  .release_nodes+0x330/0x3f0
  .device_release_driver_internal+0x178/0x2c0
  .driver_detach+0x64/0xd0
  .bus_remove_driver+0x70/0xf0
  .driver_unregister+0x38/0x80
  .platform_driver_unregister+0x14/0x30
  .fsl_sata_driver_exit+0x18/0xa20 [sata_fsl]
  .__se_sys_delete_module+0x1ec/0x2d0
  .system_call_exception+0xfc/0x1f0
  system_call_common+0xf8/0x200
 ==================================================================

The triggering of the BUG is shown in the following stack:

driver_detach
  device_release_driver_internal
    __device_release_driver
      drv->remove(dev) --> platform_drv_remove/platform_remove
        drv->remove(dev) --> sata_fsl_remove
          iounmap(host_priv->hcr_base);			<---- unmap
          kfree(host_priv);                             <---- free
      devres_release_all
        release_nodes
          dr->node.release(dev, dr->data) --> ata_host_stop
            ap->ops->port_stop(ap) --> sata_fsl_port_stop
                ioread32(hcr_base + HCONTROL)           <---- UAF
            host->ops->host_stop(host)

The iounmap(host_priv->hcr_base) and kfree(host_priv) functions should
not be executed in drv->remove. These functions should be executed in
host_stop after port_stop. Therefore, we move these functions to the
new function sata_fsl_host_stop and bind the new function to host_stop.

## References
- https://git.kernel.org/stable/c/6c8ad7e8cf29eb55836e7a0215f967746ab2b504
- https://git.kernel.org/stable/c/77393806c76b6b44f1c44bd957788c8bd9152c45
- https://git.kernel.org/stable/c/91ba94d3f7afca195b224f77a72044fbde1389ce
- https://git.kernel.org/stable/c/adf098e2a8a1e1fc075d6a5ba2edd13cf7189082
- https://git.kernel.org/stable/c/cdcd80292106df5cda325426e96495503e41f947
- https://git.kernel.org/stable/c/0769449b0a5eabc3545337217ae690e46673e73a
- https://git.kernel.org/stable/c/325ea49fc43cbc03a5e1e37de8f0ca6357ced4b1
- https://git.kernel.org/stable/c/4a46b2f5dce02539e88a300800812bd24a45e097
