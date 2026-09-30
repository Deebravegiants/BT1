# [M] nfs4: Fix kmemleak when allocate slot failed

## Summary
Severity: Medium
Advisory: CVE-2022-49927
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49927
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <4.9.333, >=4.10.0 <4.14.299, >=4.15.0 <4.19.265, >=4.20.0 <5.4.224, >=5.5.0 <5.10.154, >=5.11.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfs4: Fix kmemleak when allocate slot failed

If one of the slot allocate failed, should cleanup all the other
allocated slots, otherwise, the allocated slots will leak:

  unreferenced object 0xffff8881115aa100 (size 64):
    comm ""mount.nfs"", pid 679, jiffies 4294744957 (age 115.037s)
    hex dump (first 32 bytes):
      00 cc 19 73 81 88 ff ff 00 a0 5a 11 81 88 ff ff  ...s......Z.....
      00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    backtrace:
      [<000000007a4c434a>] nfs4_find_or_create_slot+0x8e/0x130
      [<000000005472a39c>] nfs4_realloc_slot_table+0x23f/0x270
      [<00000000cd8ca0eb>] nfs40_init_client+0x4a/0x90
      [<00000000128486db>] nfs4_init_client+0xce/0x270
      [<000000008d2cacad>] nfs4_set_client+0x1a2/0x2b0
      [<000000000e593b52>] nfs4_create_server+0x300/0x5f0
      [<00000000e4425dd2>] nfs4_try_get_tree+0x65/0x110
      [<00000000d3a6176f>] vfs_get_tree+0x41/0xf0
      [<0000000016b5ad4c>] path_mount+0x9b3/0xdd0
      [<00000000494cae71>] __x64_sys_mount+0x190/0x1d0
      [<000000005d56bdec>] do_syscall_64+0x35/0x80
      [<00000000687c9ae4>] entry_SYSCALL_64_after_hwframe+0x46/0xb0

## References
- https://git.kernel.org/stable/c/24641993a7dce6b1628645f4e1d97ca06c9f765d
- https://git.kernel.org/stable/c/45aea4fbf61e205649c29200726b9f45c1718a67
- https://git.kernel.org/stable/c/7e8436728e22181c3f12a5dbabd35ed3a8b8c593
- https://git.kernel.org/stable/c/84b5cb476903003ae9ca88f32b57ff0eaefa6d4c
- https://git.kernel.org/stable/c/86ce0e93cf6fb4d0c447323ac66577c642628b9d
- https://git.kernel.org/stable/c/925cb538bd5851154602818dc80bf4b4d924c127
- https://git.kernel.org/stable/c/aae35a0c8a775fa4afa6a4e7dab3f936f1f89bbb
- https://git.kernel.org/stable/c/db333ae981fb8843c383aa7dbf62cc682597d401
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49927.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49927
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
