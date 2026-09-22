# [H] powerpc/mm/fault: Fix kfence page fault reporting

## Summary
Severity: High
Advisory: CVE-2024-56678
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-28
Source: https://osv.dev/vulnerability/CVE-2024-56678
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/mm/fault: Fix kfence page fault reporting

copy_from_kernel_nofault() can be called when doing read of /proc/kcore.
/proc/kcore can have some unmapped kfence objects which when read via
copy_from_kernel_nofault() can cause page faults. Since *_nofault()
functions define their own fixup table for handling fault, use that
instead of asking kfence to handle such faults.

Hence we search the exception tables for the nip which generated the
fault. If there is an entry then we let the fixup table handler handle the
page fault by returning an error from within ___do_page_fault().

This can be easily triggered if someone tries to do dd from /proc/kcore.
eg. dd if=/proc/kcore of=/dev/null bs=1M

Some example false negatives:

  ===============================
  BUG: KFENCE: invalid read in copy_from_kernel_nofault+0x9c/0x1a0
  Invalid read at 0xc0000000fdff0000:
   copy_from_kernel_nofault+0x9c/0x1a0
   0xc00000000665f950
   read_kcore_iter+0x57c/0xa04
   proc_reg_read_iter+0xe4/0x16c
   vfs_read+0x320/0x3ec
   ksys_read+0x90/0x154
   system_call_exception+0x120/0x310
   system_call_vectored_common+0x15c/0x2ec

  BUG: KFENCE: use-after-free read in copy_from_kernel_nofault+0x9c/0x1a0
  Use-after-free read at 0xc0000000fe050000 (in kfence-#2):
   copy_from_kernel_nofault+0x9c/0x1a0
   0xc00000000665f950
   read_kcore_iter+0x57c/0xa04
   proc_reg_read_iter+0xe4/0x16c
   vfs_read+0x320/0x3ec
   ksys_read+0x90/0x154
   system_call_exception+0x120/0x310
   system_call_vectored_common+0x15c/0x2ec

## References
- https://git.kernel.org/stable/c/06dbbb4d5f7126b6307ab807cbf04ecfc459b933
- https://git.kernel.org/stable/c/15f78d2c3d1452645bd8b9da909b0ca266f83c43
- https://git.kernel.org/stable/c/4d2655754e94741b159aa807b72ea85518a65fd5
- https://git.kernel.org/stable/c/7eaeb7a49b6d16640f9f3c9074c05175d74c710b
- https://git.kernel.org/stable/c/9ea8d8bf9b625e8ad3be6b0432aecdc549914121
- https://git.kernel.org/stable/c/e0a470b5733c1fe068d5c58b0bb91ad539604bc6
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56678.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56678
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
