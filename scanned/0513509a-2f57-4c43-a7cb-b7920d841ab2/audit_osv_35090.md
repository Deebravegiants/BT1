# [C] ksmbd: ipc: fix use-after-free in ipc_msg_send_request

## Summary
Severity: Critical
Advisory: CVE-2025-68263
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68263
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.62, >=6.13.0 <6.17.12, >=6.18.0 <6.18.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: ipc: fix use-after-free in ipc_msg_send_request

ipc_msg_send_request() waits for a generic netlink reply using an
ipc_msg_table_entry on the stack. The generic netlink handler
(handle_generic_event()/handle_response()) fills entry->response under
ipc_msg_table_lock, but ipc_msg_send_request() used to validate and free
entry->response without holding the same lock.

Under high concurrency this allows a race where handle_response() is
copying data into entry->response while ipc_msg_send_request() has just
freed it, leading to a slab-use-after-free reported by KASAN in
handle_generic_event():

  BUG: KASAN: slab-use-after-free in handle_generic_event+0x3c4/0x5f0 [ksmbd]
  Write of size 12 at addr ffff888198ee6e20 by task pool/109349
  ...
  Freed by task:
    kvfree
    ipc_msg_send_request [ksmbd]
    ksmbd_rpc_open -> ksmbd_session_rpc_open [ksmbd]

Fix by:
- Taking ipc_msg_table_lock in ipc_msg_send_request() while validating
  entry->response, freeing it when invalid, and removing the entry from
  ipc_msg_table.
- Returning the final entry->response pointer to the caller only after
  the hash entry is removed under the lock.
- Returning NULL in the error path, preserving the original API
  semantics.

This makes all accesses to entry->response consistent with
handle_response(), which already updates and fills the response buffer
under ipc_msg_table_lock, and closes the race that allowed the UAF.

## References
- https://git.kernel.org/stable/c/1fab1fa091f5aa97265648b53ea031deedd26235
- https://git.kernel.org/stable/c/5ac763713a1ef8f9a8bda1dbd81f0318d67baa4e
- https://git.kernel.org/stable/c/708a620b471a14466f1f52c90bf3f65ebdb31460
- https://git.kernel.org/stable/c/759c8c30cfa8706c518e56f67971b1f0932f4b9b
- https://git.kernel.org/stable/c/8229c6ca50cea701e25a7ee25f48441b582ec5fa
- https://git.kernel.org/stable/c/de85fb58f9967ba024bb08e0041613d37b57b4d1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68263.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68263
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
