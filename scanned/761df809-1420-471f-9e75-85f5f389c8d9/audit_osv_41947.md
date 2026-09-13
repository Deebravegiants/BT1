# [H] ksmbd: fix null pointer dereference in proc_show_files()

## Summary
Severity: High
Advisory: CVE-2026-64140
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64140
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix null pointer dereference in proc_show_files()

When a SMB2 client opens a file with a durable v2 handle and then issues
SMB2 SESSION_LOGOFF, session_fd_check() clears fp->tcon = NULL on the
reconnectable file pointer but leaves the fp registered in global_ft.idr
until the durable scavenger fires (up to fp->durable_timeout seconds
later).

During that window any read of /proc/fs/ksmbd/files (mode 0400) panics
the kernel because proc_show_files() walks global_ft.idr and
unconditionally dereferences fp->tcon->id with no NULL guard.

Reproducer requires only a successful SMB2 SESSION_SETUP and a share
configured with 'durable handles = yes'. KASAN report on mainline
70390501d194:

  general protection fault, probably for non-canonical address
  0xdffffc0000000000: 0000 [#1] SMP KASAN PTI
  KASAN: null-ptr-deref in range [0x0000000000000000-0x0000000000000007]
  RIP: 0010:proc_show_files+0x118/0x740
  Call Trace:
   proc_show_files+0x118/0x740
   seq_read_iter+0x4ef/0xe10
   proc_reg_read_iter+0x1b7/0x280
   ...

Guard the dereference. A durable-disconnected fp legitimately has no
tcon; report its tree id as 0 rather than oopsing.

## References
- https://git.kernel.org/stable/c/8eab081627b67216d1c8f638b68289b500dc9a6b
- https://git.kernel.org/stable/c/904901561e61a2b559070b20c74a8c95491f30aa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64140.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64140
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
