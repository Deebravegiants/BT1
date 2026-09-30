# [C] ksmbd: fix use-after-free of conn->preauth_info in concurrent SMB2 NEGOTIATE

## Summary
Severity: Critical
Advisory: CVE-2026-72422
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72422
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.212, >=5.16.0 <6.1.178, >=6.0.0 <6.6.145, >=6.2.0 <6.12.97, >=6.7.0 <6.18.40, >=6.13.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free of conn->preauth_info in concurrent SMB2 NEGOTIATE

conn->preauth_info is shared connection state (struct
preauth_integrity_info, kmalloc-96) that is allocated and freed by the
SMB2 NEGOTIATE handler and read by the response send path.

smb2_handle_negotiate() allocates conn->preauth_info, and on a
deassemble_neg_contexts() failure kfrees it and sets it to NULL. Both the
allocation and the free/NULL happen under ksmbd_conn_lock(conn) (the
connection srv_mutex), which is held across the whole handler body.

The response send path smb3_preauth_hash_rsp(), called from the send:
block of __handle_ksmbd_work(), reads conn->preauth_info and dereferences
conn->preauth_info->Preauth_HashValue (via
ksmbd_gen_preauth_integrity_hash()) without taking conn_lock. When a
client drives two SMB2 NEGOTIATE requests on the same connection, one
worker can free conn->preauth_info on the failing-negotiate path while a
concurrent send-path worker is reading it, producing a slab
use-after-free read (KASAN-confirmed).

The send-path read tested conn->preauth_info for NULL but raced with the
free that occurs between the NULL check and the dereference, so the NULL
guard alone does not close the window.

Serialize the NEGOTIATE-branch read in smb3_preauth_hash_rsp() under
ksmbd_conn_lock(conn) and re-check conn->preauth_info inside the lock.
Because the negotiate handler holds conn_lock across its kfree + NULL
assignment, a reader that also takes conn_lock either runs fully before
the allocation or fully after the NULL store, and can never observe the
freed-but-not-yet-NULLed pointer. ksmbd_gen_preauth_integrity_hash()
takes no locks itself (it only computes a SHA-512 over the buffer), so
no lock-ordering inversion is introduced, and conn_lock is a sleepable
mutex which is safe on this send path (it already performs network I/O).

## References
- https://git.kernel.org/stable/c/0c054227479ed7e36ebccb3a558bc0ef698264f6
- https://git.kernel.org/stable/c/16a1ecf39c217e3d164bd32ef2a4f650abc067fa
- https://git.kernel.org/stable/c/1c89da3baa2b1f269178afa87dc30479b8535776
- https://git.kernel.org/stable/c/7470511d085af1c7a043a60e53d52b512d5a10b1
- https://git.kernel.org/stable/c/77bb0bbfcc4e777ca653174689e5e363f8ee63d1
- https://git.kernel.org/stable/c/c7bef84740d1d57848c74f6f5b996606e43ea4fe
- https://git.kernel.org/stable/c/d0a469122e7bf8338fec1949fb1e8e1290ed8caa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72422.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72422
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
