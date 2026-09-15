# [H] fscrypt: Avoid dynamic allocation in fscrypt_get_devices()

## Summary
Severity: High
Advisory: CVE-2026-68147
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68147
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

fscrypt: Avoid dynamic allocation in fscrypt_get_devices()

When a blk_crypto_key starts being used or is evicted, fs/crypto/ calls
fscrypt_get_devices() to get the filesystem's list of block devices,
then iterates over them and calls blk_crypto_config_supported(),
blk_crypto_start_using_key(), or blk_crypto_evict_key() on each one.

Currently, the block device pointers are placed in a dynamically
allocated array.  This dynamic allocation is problematic because:

- It can fail, especially at the fscrypt_destroy_inline_crypt_key() call
  site when it's invoked for inode eviction under direct reclaim.

- fscrypt_destroy_inline_crypt_key() doesn't handle the failure.  It
  just zeroizes and frees the blk_crypto_key without calling
  blk_crypto_evict_key().  That causes a use-after-free.

For now, let's fix this in the straightforward and easily-backportable
way by switching to an on-stack array.  Currently the fscrypt
multi-device functionality is used only by f2fs, which has a hardcoded
limit of 8 block devices.  An on-stack array works fine for that.

(Of course, this solution won't scale up to large number of block
devices.  For that we'd need a different solution, like moving the block
device iteration into the filesystem.  Or in the case of btrfs, which
will only support blk-crypto-fallback, we should make it just call
blk-crypto-fallback directly, so the block devices won't be needed.)

## References
- https://git.kernel.org/stable/c/4462ac3d90e897dda52ce4b6af2d526ddae835a8
- https://git.kernel.org/stable/c/6fe4e4b8259e1330945b5f3c9476e08473b8e0e8
- https://git.kernel.org/stable/c/81ea8e8221853950c47dac7164f27c63a96f8f86
- https://git.kernel.org/stable/c/97a688563be71ec6fefc071aff69a66c69dbe244
- https://git.kernel.org/stable/c/bab016bb80d74a9d1f7d4121a7fc1cb529b470e0
- https://git.kernel.org/stable/c/bc2d630296e0e049210ec05ff08459a6893ae749
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68147.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68147
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
