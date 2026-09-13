# [H] greybus: raw: fix use-after-free if write is called after disconnect

## Summary
Severity: High
Advisory: CVE-2026-53024
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53024
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

greybus: raw: fix use-after-free if write is called after disconnect

If a user writes to the chardev after disconnect has been called, the
kernel panics with the following trace (with
CONFIG_INIT_ON_FREE_DEFAULT_ON=y):

        BUG: kernel NULL pointer dereference, address: 0000000000000218
         ...
        Call Trace:
         <TASK>
         gb_operation_create_common+0x61/0x180
         gb_operation_create_flags+0x28/0xa0
         gb_operation_sync_timeout+0x6f/0x100
         raw_write+0x7b/0xc7 [gb_raw]
         vfs_write+0xcf/0x420
         ? task_mm_cid_work+0x136/0x220
         ksys_write+0x63/0xe0
         do_syscall_64+0xa4/0x290
         entry_SYSCALL_64_after_hwframe+0x77/0x7f

Disconnect calls gb_connection_destroy, which ends up freeing the
connection object. When gb_operation_sync is called in the write file
operations, its gets a freed connection as parameter and the kernel
panics.

The gb_connection_destroy cannot be moved out of the disconnect
function, as the Greybus subsystem expect all connections belonging to a
bundle to be destroyed when disconnect returns.

To prevent this bug, use a rw lock to synchronize access between write
and disconnect. This guarantees that the write function doesn't try
to use a disconnected connection.

## References
- https://git.kernel.org/stable/c/48d6c32bc049abd114e8f0836c0e7d7cbfba7827
- https://git.kernel.org/stable/c/84265cbd96b97058ef67e3f8be3933667a000835
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53024.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53024
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
