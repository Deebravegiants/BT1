# [C] smb: client: fix use-after-free in crypt_message when using async crypto

## Summary
Severity: Critical
Advisory: CVE-2025-38488
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-28
Source: https://osv.dev/vulnerability/CVE-2025-38488
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.147, >=6.2.0 <6.6.100, >=6.7.0 <6.12.40, >=6.12.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix use-after-free in crypt_message when using async crypto

The CVE-2024-50047 fix removed asynchronous crypto handling from
crypt_message(), assuming all crypto operations are synchronous.
However, when hardware crypto accelerators are used, this can cause
use-after-free crashes:

  crypt_message()
    // Allocate the creq buffer containing the req
    creq = smb2_get_aead_req(..., &req);

    // Async encryption returns -EINPROGRESS immediately
    rc = enc ? crypto_aead_encrypt(req) : crypto_aead_decrypt(req);

    // Free creq while async operation is still in progress
    kvfree_sensitive(creq, ...);

Hardware crypto modules often implement async AEAD operations for
performance. When crypto_aead_encrypt/decrypt() returns -EINPROGRESS,
the operation completes asynchronously. Without crypto_wait_req(),
the function immediately frees the request buffer, leading to crashes
when the driver later accesses the freed memory.

This results in a use-after-free condition when the hardware crypto
driver later accesses the freed request structure, leading to kernel
crashes with NULL pointer dereferences.

The issue occurs because crypto_alloc_aead() with mask=0 doesn't
guarantee synchronous operation. Even without CRYPTO_ALG_ASYNC in
the mask, async implementations can be selected.

Fix by restoring the async crypto handling:
- DECLARE_CRYPTO_WAIT(wait) for completion tracking
- aead_request_set_callback() for async completion notification
- crypto_wait_req() to wait for operation completion

This ensures the request buffer isn't freed until the crypto operation
completes, whether synchronous or asynchronous, while preserving the
CVE-2024-50047 fix.

## References
- https://git.kernel.org/stable/c/15a0a5de49507062bc3be4014a403d8cea5533de
- https://git.kernel.org/stable/c/2a76bc2b24ed889a689fb1c9015307bf16aafb5b
- https://git.kernel.org/stable/c/5d047b12f86cc3b9fde1171c02d9bccf4dba0632
- https://git.kernel.org/stable/c/6550b2bef095d0dd2d2c8390d2ea4c3837028833
- https://git.kernel.org/stable/c/8ac90f6824fc44d2e55a82503ddfc95defb19ae0
- https://git.kernel.org/stable/c/9a1d3e8d40f151c2d5a5f40c410e6e433f62f438
- https://git.kernel.org/stable/c/b220bed63330c0e1733dc06ea8e75d5b9962b6b6
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38488.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38488
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
