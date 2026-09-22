# [H] ksmbd: Fix race condition in RPC handle list access

## Summary
Severity: High
Advisory: CVE-2025-40039
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40039
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.123, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: Fix race condition in RPC handle list access

The 'sess->rpc_handle_list' XArray manages RPC handles within a ksmbd
session. Access to this list is intended to be protected by
'sess->rpc_lock' (an rw_semaphore). However, the locking implementation was
flawed, leading to potential race conditions.

In ksmbd_session_rpc_open(), the code incorrectly acquired only a read lock
before calling xa_store() and xa_erase(). Since these operations modify
the XArray structure, a write lock is required to ensure exclusive access
and prevent data corruption from concurrent modifications.

Furthermore, ksmbd_session_rpc_method() accessed the list using xa_load()
without holding any lock at all. This could lead to reading inconsistent
data or a potential use-after-free if an entry is concurrently removed and
the pointer is dereferenced.

Fix these issues by:
1. Using down_write() and up_write() in ksmbd_session_rpc_open()
   to ensure exclusive access during XArray modification, and ensuring
   the lock is correctly released on error paths.
2. Adding down_read() and up_read() in ksmbd_session_rpc_method()
   to safely protect the lookup.

## References
- https://git.kernel.org/stable/c/305853cce379407090a73b38c5de5ba748893aee
- https://git.kernel.org/stable/c/5cc679ba0f4505936124cd4179ba66bb0a4bd9f3
- https://git.kernel.org/stable/c/69674b029002b1d90b655f014bdf64f404efa54d
- https://git.kernel.org/stable/c/6b615a8fb3af0baf8126cde3d4fee97d57222ffc
- https://git.kernel.org/stable/c/6bd7e0e55dcea2cf0d391bbc21c2eb069b4be3e1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40039.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40039
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
