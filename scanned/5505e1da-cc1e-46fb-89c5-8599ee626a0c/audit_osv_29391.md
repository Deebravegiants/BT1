# [H] cifs: Fix server re-repick on subrequest retry

## Summary
Severity: High
Advisory: CVE-2024-42256
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-08
Source: https://osv.dev/vulnerability/CVE-2024-42256
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.10.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: Fix server re-repick on subrequest retry

When a subrequest is marked for needing retry, netfs will call
cifs_prepare_write() which will make cifs repick the server for the op
before renegotiating credits; it then calls cifs_issue_write() which
invokes smb2_async_writev() - which re-repicks the server.

If a different server is then selected, this causes the increment of
server->in_flight to happen against one record and the decrement to happen
against another, leading to misaccounting.

Fix this by just removing the repick code in smb2_async_writev().  As this
is only called from netfslib-driven code, cifs_prepare_write() should
always have been called first, and so server should never be NULL and the
preparatory step is repeated in the event that we do a retry.

The problem manifests as a warning looking something like:

 WARNING: CPU: 4 PID: 72896 at fs/smb/client/smb2ops.c:97 smb2_add_credits+0x3f0/0x9e0 [cifs]
 ...
 RIP: 0010:smb2_add_credits+0x3f0/0x9e0 [cifs]
 ...
  smb2_writev_callback+0x334/0x560 [cifs]
  cifs_demultiplex_thread+0x77a/0x11b0 [cifs]
  kthread+0x187/0x1d0
  ret_from_fork+0x34/0x60
  ret_from_fork_asm+0x1a/0x30

Which may be triggered by a number of different xfstests running against an
Azure server in multichannel mode.  generic/249 seems the most repeatable,
but generic/215, generic/249 and generic/308 may also show it.

## References
- https://git.kernel.org/stable/c/b1d0a566769b6fb3795b5289fc1daf9e0638d97a
- https://git.kernel.org/stable/c/de40579b903883274fe203865f29d66b168b7236
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42256.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42256
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
