# [M] net: hns3: fix kernel crash when uninstalling driver

## Summary
Severity: Medium
Advisory: CVE-2024-50296
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50296
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.172, >=5.15.0 <6.1.117, >=5.16.0 <6.6.61, >=6.2.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: hns3: fix kernel crash when uninstalling driver

When the driver is uninstalled and the VF is disabled concurrently, a
kernel crash occurs. The reason is that the two actions call function
pci_disable_sriov(). The num_VFs is checked to determine whether to
release the corresponding resources. During the second calling, num_VFs
is not 0 and the resource release function is called. However, the
corresponding resource has been released during the first invoking.
Therefore, the problem occurs:

[15277.839633][T50670] Unable to handle kernel NULL pointer dereference at virtual address 0000000000000020
...
[15278.131557][T50670] Call trace:
[15278.134686][T50670]  klist_put+0x28/0x12c
[15278.138682][T50670]  klist_del+0x14/0x20
[15278.142592][T50670]  device_del+0xbc/0x3c0
[15278.146676][T50670]  pci_remove_bus_device+0x84/0x120
[15278.151714][T50670]  pci_stop_and_remove_bus_device+0x6c/0x80
[15278.157447][T50670]  pci_iov_remove_virtfn+0xb4/0x12c
[15278.162485][T50670]  sriov_disable+0x50/0x11c
[15278.166829][T50670]  pci_disable_sriov+0x24/0x30
[15278.171433][T50670]  hnae3_unregister_ae_algo_prepare+0x60/0x90 [hnae3]
[15278.178039][T50670]  hclge_exit+0x28/0xd0 [hclge]
[15278.182730][T50670]  __se_sys_delete_module.isra.0+0x164/0x230
[15278.188550][T50670]  __arm64_sys_delete_module+0x1c/0x30
[15278.193848][T50670]  invoke_syscall+0x50/0x11c
[15278.198278][T50670]  el0_svc_common.constprop.0+0x158/0x164
[15278.203837][T50670]  do_el0_svc+0x34/0xcc
[15278.207834][T50670]  el0_svc+0x20/0x30

For details, see the following figure.

     rmmod hclge              disable VFs
----------------------------------------------------
hclge_exit()            sriov_numvfs_store()
  ...                     device_lock()
  pci_disable_sriov()     hns3_pci_sriov_configure()
                            pci_disable_sriov()
                              sriov_disable()
    sriov_disable()             if !num_VFs :
      if !num_VFs :               return;
        return;                 sriov_del_vfs()
      sriov_del_vfs()             ...
        ...                       klist_put()
        klist_put()               ...
        ...                     num_VFs = 0;
      num_VFs = 0;        device_unlock();

In this patch, when driver is removing, we get the device_lock()
to protect num_VFs, just like sriov_numvfs_store().

## References
- https://git.kernel.org/stable/c/590a4b2d4e0b73586e88bce9b8135b593355ec09
- https://git.kernel.org/stable/c/719edd9f3372ce7fb3b157647c6658672946874b
- https://git.kernel.org/stable/c/76b155e14d9b182ce83d32ada2d0d7219ea8c8dd
- https://git.kernel.org/stable/c/7ae4e56de7dbd0999578246a536cf52a63f4056d
- https://git.kernel.org/stable/c/a0df055775f30850c0da8f7dab40d67c0fd63908
- https://git.kernel.org/stable/c/b5c94e4d947d15d521e935ff10c5a22a7883dea5
- https://git.kernel.org/stable/c/df3dff8ab6d79edc942464999d06fbaedf8cdd18
- https://git.kernel.org/stable/c/e36482b222e00cc7aeeea772fc0cf2943590bc4d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50296.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50296
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
