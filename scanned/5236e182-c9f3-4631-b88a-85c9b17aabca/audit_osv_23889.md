# [H] sfc: fix use after free when disabling sriov

## Summary
Severity: High
Advisory: CVE-2022-49626
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49626
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.9.324, >=4.10.0 <4.14.289, >=4.15.0 <4.19.253, >=4.20.0 <5.4.207, >=5.5.0 <5.10.132, >=5.11.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

sfc: fix use after free when disabling sriov

Use after free is detected by kfence when disabling sriov. What was read
after being freed was vf->pci_dev: it was freed from pci_disable_sriov
and later read in efx_ef10_sriov_free_vf_vports, called from
efx_ef10_sriov_free_vf_vswitching.

Set the pointer to NULL at release time to not trying to read it later.

Reproducer and dmesg log (note that kfence doesn't detect it every time):
$ echo 1 > /sys/class/net/enp65s0f0np0/device/sriov_numvfs
$ echo 0 > /sys/class/net/enp65s0f0np0/device/sriov_numvfs

 BUG: KFENCE: use-after-free read in efx_ef10_sriov_free_vf_vswitching+0x82/0x170 [sfc]

 Use-after-free read at 0x00000000ff3c1ba5 (in kfence-#224):
  efx_ef10_sriov_free_vf_vswitching+0x82/0x170 [sfc]
  efx_ef10_pci_sriov_disable+0x38/0x70 [sfc]
  efx_pci_sriov_configure+0x24/0x40 [sfc]
  sriov_numvfs_store+0xfe/0x140
  kernfs_fop_write_iter+0x11c/0x1b0
  new_sync_write+0x11f/0x1b0
  vfs_write+0x1eb/0x280
  ksys_write+0x5f/0xe0
  do_syscall_64+0x5c/0x80
  entry_SYSCALL_64_after_hwframe+0x44/0xae

 kfence-#224: 0x00000000edb8ef95-0x00000000671f5ce1, size=2792, cache=kmalloc-4k

 allocated by task 6771 on cpu 10 at 3137.860196s:
  pci_alloc_dev+0x21/0x60
  pci_iov_add_virtfn+0x2a2/0x320
  sriov_enable+0x212/0x3e0
  efx_ef10_sriov_configure+0x67/0x80 [sfc]
  efx_pci_sriov_configure+0x24/0x40 [sfc]
  sriov_numvfs_store+0xba/0x140
  kernfs_fop_write_iter+0x11c/0x1b0
  new_sync_write+0x11f/0x1b0
  vfs_write+0x1eb/0x280
  ksys_write+0x5f/0xe0
  do_syscall_64+0x5c/0x80
  entry_SYSCALL_64_after_hwframe+0x44/0xae

 freed by task 6771 on cpu 12 at 3170.991309s:
  device_release+0x34/0x90
  kobject_cleanup+0x3a/0x130
  pci_iov_remove_virtfn+0xd9/0x120
  sriov_disable+0x30/0xe0
  efx_ef10_pci_sriov_disable+0x57/0x70 [sfc]
  efx_pci_sriov_configure+0x24/0x40 [sfc]
  sriov_numvfs_store+0xfe/0x140
  kernfs_fop_write_iter+0x11c/0x1b0
  new_sync_write+0x11f/0x1b0
  vfs_write+0x1eb/0x280
  ksys_write+0x5f/0xe0
  do_syscall_64+0x5c/0x80
  entry_SYSCALL_64_after_hwframe+0x44/0xae

## References
- https://git.kernel.org/stable/c/3199e34912d84cdfb8a93a984c5ae5c73fb13e84
- https://git.kernel.org/stable/c/58d93e9d160c0de6d867c7eb4c2206671a351eb1
- https://git.kernel.org/stable/c/9c854ae512b89229aeee93849e9bd4c115b37909
- https://git.kernel.org/stable/c/bcad880865bfb421885364b1f0c7351280fe2b97
- https://git.kernel.org/stable/c/c2240500817b3b4b996cdf2a461a3a5679f49b94
- https://git.kernel.org/stable/c/c9e75bb22a26e391f189f5a5133dd63dcb57fdaa
- https://git.kernel.org/stable/c/e435c4aeeaa073091f7f3b7735af2ef5c97d63f2
- https://git.kernel.org/stable/c/ebe41da5d47ac0fff877e57bd14c54dccf168827
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49626.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49626
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
