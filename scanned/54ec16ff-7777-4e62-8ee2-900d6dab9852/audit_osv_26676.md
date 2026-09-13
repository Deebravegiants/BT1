# [H] blk-crypto: make blk_crypto_evict_key() more robust

## Summary
Severity: High
Advisory: CVE-2023-53536
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53536
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

blk-crypto: make blk_crypto_evict_key() more robust

If blk_crypto_evict_key() sees that the key is still in-use (due to a
bug) or that ->keyslot_evict failed, it currently just returns while
leaving the key linked into the keyslot management structures.

However, blk_crypto_evict_key() is only called in contexts such as inode
eviction where failure is not an option.  So actually the caller
proceeds with freeing the blk_crypto_key regardless of the return value
of blk_crypto_evict_key().

These two assumptions don't match, and the result is that there can be a
use-after-free in blk_crypto_reprogram_all_keys() after one of these
errors occurs.  (Note, these errors *shouldn't* happen; we're just
talking about what happens if they do anyway.)

Fix this by making blk_crypto_evict_key() unlink the key from the
keyslot management structures even on failure.

Also improve some comments.

## References
- https://git.kernel.org/stable/c/5bb4005fb667c6e2188fa87950f8d5faf2994410
- https://git.kernel.org/stable/c/5c62852942667c613de0458fc797c5b8c36112b5
- https://git.kernel.org/stable/c/5c7cb94452901a93e90c2230632e2c12a681bc92
- https://git.kernel.org/stable/c/64ef787bb1588475163069c2e62fdd8f6c27b1f6
- https://git.kernel.org/stable/c/701a8220762ff90615dc91d3543f789391b63298
- https://git.kernel.org/stable/c/809a5be62e92a444a3c3d7b9f438019d0b322f55
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53536.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53536
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
