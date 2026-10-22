# [M] CVE-2021-47631

## Summary
Severity: Medium
Advisory: CVE-2021-47631
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47631
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ARM: davinci: da850-evm: Avoid NULL pointer dereference

With newer versions of GCC, there is a panic in da850_evm_config_emac()
when booting multi_v5_defconfig in QEMU under the palmetto-bmc machine:

Unable to handle kernel NULL pointer dereference at virtual address 00000020
pgd = (ptrval)
[00000020] *pgd=00000000
Internal error: Oops: 5 [#1] PREEMPT ARM
Modules linked in:
CPU: 0 PID: 1 Comm: swapper Not tainted 5.15.0 #1
Hardware name: Generic DT based system
PC is at da850_evm_config_emac+0x1c/0x120
LR is at do_one_initcall+0x50/0x1e0

The emac_pdata pointer in soc_info is NULL because davinci_soc_info only
gets populated on davinci machines but da850_evm_config_emac() is called
on all machines via device_initcall().

Move the rmii_en assignment below the machine check so that it is only
dereferenced when running on a supported SoC.

## References
- https://git.kernel.org/stable/c/0940795c6834fbe7705acc5c3d4b2f7a5f67527a
- https://git.kernel.org/stable/c/0a312ec66a03133d28570f07bc52749ccfef54da
- https://git.kernel.org/stable/c/83a1cde5c74bfb44b49cb2a940d044bb2380f4ea
- https://git.kernel.org/stable/c/89931d4762572aaee6edbe5673d41f8082de110f
- https://git.kernel.org/stable/c/a12b356d45cbb6e8a1b718d1436b3d6239a862f3
- https://git.kernel.org/stable/c/c06f476e5b74bcabb8c4a2fba55864a37e62843b
- https://git.kernel.org/stable/c/c5628533a3ece64235d04fe11ec44d2be99e423d
- https://git.kernel.org/stable/c/c64e2ed5cc376e137e572babfd2edc38b2cfb61b
