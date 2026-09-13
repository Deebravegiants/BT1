# [H] blk-mq: release crypto keyslot before reporting I/O complete

## Summary
Severity: High
Advisory: CVE-2023-53810
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53810
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

blk-mq: release crypto keyslot before reporting I/O complete

Once all I/O using a blk_crypto_key has completed, filesystems can call
blk_crypto_evict_key().  However, the block layer currently doesn't call
blk_crypto_put_keyslot() until the request is being freed, which happens
after upper layers have been told (via bio_endio()) the I/O has
completed.  This causes a race condition where blk_crypto_evict_key()
can see 'slot_refs != 0' without there being an actual bug.

This makes __blk_crypto_evict_key() hit the
'WARN_ON_ONCE(atomic_read(&slot->slot_refs) != 0)' and return without
doing anything, eventually causing a use-after-free in
blk_crypto_reprogram_all_keys().  (This is a very rare bug and has only
been seen when per-file keys are being used with fscrypt.)

There are two options to fix this: either release the keyslot before
bio_endio() is called on the request's last bio, or make
__blk_crypto_evict_key() ignore slot_refs.  Let's go with the first
solution, since it preserves the ability to report bugs (via
WARN_ON_ONCE) where a key is evicted while still in-use.

## References
- https://git.kernel.org/stable/c/7d206ec7a04e8545828191b6ea8b49d3ea61391f
- https://git.kernel.org/stable/c/874bdf43b4a7dc5463c31508f62b3e42eb237b08
- https://git.kernel.org/stable/c/92d5d233b9ff531cf9cc36ab4251779e07adb633
- https://git.kernel.org/stable/c/9cd1e566676bbcb8a126acd921e4e194e6339603
- https://git.kernel.org/stable/c/b278570e2c59d538216f8b656e97680188a8fba4
- https://git.kernel.org/stable/c/d206f79d9cd658665b37ce8134c6ec849ac7af0c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53810.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53810
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
