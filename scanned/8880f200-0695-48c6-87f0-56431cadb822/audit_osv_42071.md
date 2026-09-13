# [C] crypto: krb5 - filter out async aead implementations at alloc

## Summary
Severity: Critical
Advisory: CVE-2026-64439
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64439
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: krb5 - filter out async aead implementations at alloc

krb5_aead_encrypt(), krb5_aead_decrypt() in rfc3961_simplified.c and
rfc8009_encrypt(), rfc8009_decrypt() in rfc8009_aes2.c set a NULL
completion callback and treat any negative return from
crypto_aead_{encrypt,decrypt}() as terminal, falling through to
kfree_sensitive(buffer).  When the encrypt_name resolves to an
async AEAD instance the request returns -EINPROGRESS, the buffer
is freed while the backend's worker still holds a pointer, and the
worker dereferences the freed slab on completion.

KASAN report under UML+SLUB with a synthetic async aead backend
bound to krb5->encrypt_name:

  BUG: KASAN: slab-use-after-free in t5_stub_complete+0x7d/0xc7

The helpers were written synchronously, so filter the async
instances out at allocation time instead of plumbing
crypto_wait_req() through every call site.

Reachable via net/rxrpc/rxgk.c, fs/afs/cm_security.c and
net/ceph/crypto.c on systems with an async AEAD provider bound to
the krb5 enctype name.

## References
- https://git.kernel.org/stable/c/2b7bd6dccff14b8b632c5244f1fd506918077221
- https://git.kernel.org/stable/c/6c9dddeb582fde005360f4fe02c760d45ca05fb5
- https://git.kernel.org/stable/c/ef6feb77e2d91761427c5b773edc9c97e1b706ad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64439.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64439
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
