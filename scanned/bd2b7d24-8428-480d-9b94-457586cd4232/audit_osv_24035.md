# [H] fscrypt: stop using keyrings subsystem for fscrypt_master_key

## Summary
Severity: High
Advisory: CVE-2022-49899
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49899
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.10.154, >=5.11.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

fscrypt: stop using keyrings subsystem for fscrypt_master_key

The approach of fs/crypto/ internally managing the fscrypt_master_key
structs as the payloads of "struct key" objects contained in a
"struct key" keyring has outlived its usefulness.  The original idea was
to simplify the code by reusing code from the keyrings subsystem.
However, several issues have arisen that can't easily be resolved:

- When a master key struct is destroyed, blk_crypto_evict_key() must be
  called on any per-mode keys embedded in it.  (This started being the
  case when inline encryption support was added.)  Yet, the keyrings
  subsystem can arbitrarily delay the destruction of keys, even past the
  time the filesystem was unmounted.  Therefore, currently there is no
  easy way to call blk_crypto_evict_key() when a master key is
  destroyed.  Currently, this is worked around by holding an extra
  reference to the filesystem's request_queue(s).  But it was overlooked
  that the request_queue reference is *not* guaranteed to pin the
  corresponding blk_crypto_profile too; for device-mapper devices that
  support inline crypto, it doesn't.  This can cause a use-after-free.

- When the last inode that was using an incompletely-removed master key
  is evicted, the master key removal is completed by removing the key
  struct from the keyring.  Currently this is done via key_invalidate().
  Yet, key_invalidate() takes the key semaphore.  This can deadlock when
  called from the shrinker, since in fscrypt_ioctl_add_key(), memory is
  allocated with GFP_KERNEL under the same semaphore.

- More generally, the fact that the keyrings subsystem can arbitrarily
  delay the destruction of keys (via garbage collection delay, or via
  random processes getting temporary key references) is undesirable, as
  it means we can't strictly guarantee that all secrets are ever wiped.

- Doing the master key lookups via the keyrings subsystem results in the
  key_permission LSM hook being called.  fscrypt doesn't want this, as
  all access control for encrypted files is designed to happen via the
  files themselves, like any other files.  The workaround which SELinux
  users are using is to change their SELinux policy to grant key search
  access to all domains.  This works, but it is an odd extra step that
  shouldn't really have to be done.

The fix for all these issues is to change the implementation to what I
should have done originally: don't use the keyrings subsystem to keep
track of the filesystem's fscrypt_master_key structs.  Instead, just
store them in a regular kernel data structure, and rework the reference
counting, locking, and lifetime accordingly.  Retain support for
RCU-mode key lookups by using a hash table.  Replace fscrypt_sb_free()
with fscrypt_sb_delete(), which releases the keys synchronously and runs
a bit earlier during unmount, so that block devices are still available.

A side effect of this patch is that neither the master keys themselves
nor the filesystem keyrings will be listed in /proc/keys anymore.
("Master key users" and the master key users keyrings will still be
listed.)  However, this was mostly an implementation detail, and it was
intended just for debugging purposes.  I don't know of anyone using it.

This patch does *not* change how "master key users" (->mk_users) works;
that still uses the keyrings subsystem.  That is still needed for key
quotas, and changing that isn't necessary to solve the issues listed
above.  If we decide to change that too, it would be a separate patch.

I've marked this as fixing the original commit that added the fscrypt
keyring, but as noted above the most important issue that this patch
fixes wasn't introduced until the addition of inline encryption support.

## References
- https://git.kernel.org/stable/c/391cceee6d435e616f68631e68f5b32d480b1e67
- https://git.kernel.org/stable/c/68d15d6558a386f46d815a6ac39edecad713a1bf
- https://git.kernel.org/stable/c/d7e7b9af104c7b389a0c21eb26532511bce4b510
- https://git.kernel.org/stable/c/e6f4fd85ef1ee6ab356bfbd64df28c1cb73aee7e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49899.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49899
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
