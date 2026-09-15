# [M] cifs: Fix memory leak when build ntlmssp negotiate blob failed

## Summary
Severity: Medium
Advisory: CVE-2022-50372
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50372
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.0.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: Fix memory leak when build ntlmssp negotiate blob failed

There is a memory leak when mount cifs:
  unreferenced object 0xffff888166059600 (size 448):
    comm "mount.cifs", pid 51391, jiffies 4295596373 (age 330.596s)
    hex dump (first 32 bytes):
      fe 53 4d 42 40 00 00 00 00 00 00 00 01 00 82 00  .SMB@...........
      00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    backtrace:
      [<0000000060609a61>] mempool_alloc+0xe1/0x260
      [<00000000adfa6c63>] cifs_small_buf_get+0x24/0x60
      [<00000000ebb404c7>] __smb2_plain_req_init+0x32/0x460
      [<00000000bcf875b4>] SMB2_sess_alloc_buffer+0xa4/0x3f0
      [<00000000753a2987>] SMB2_sess_auth_rawntlmssp_negotiate+0xf5/0x480
      [<00000000f0c1f4f9>] SMB2_sess_setup+0x253/0x410
      [<00000000a8b83303>] cifs_setup_session+0x18f/0x4c0
      [<00000000854bd16d>] cifs_get_smb_ses+0xae7/0x13c0
      [<000000006cbc43d9>] mount_get_conns+0x7a/0x730
      [<000000005922d816>] cifs_mount+0x103/0xd10
      [<00000000e33def3b>] cifs_smb3_do_mount+0x1dd/0xc90
      [<0000000078034979>] smb3_get_tree+0x1d5/0x300
      [<000000004371f980>] vfs_get_tree+0x41/0xf0
      [<00000000b670d8a7>] path_mount+0x9b3/0xdd0
      [<000000005e839a7d>] __x64_sys_mount+0x190/0x1d0
      [<000000009404c3b9>] do_syscall_64+0x35/0x80

When build ntlmssp negotiate blob failed, the session setup request
should be freed.

## References
- https://git.kernel.org/stable/c/30b2d7f8f13664655480d6af45f60270b3eb6736
- https://git.kernel.org/stable/c/fa5a70bdd5e565c8696fb04dfe18a4e8aff4695d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50372.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50372
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
