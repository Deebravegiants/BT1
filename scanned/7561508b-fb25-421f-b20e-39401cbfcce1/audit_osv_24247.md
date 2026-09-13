# [H] ext4: fix deadlock due to mbcache entry corruption

## Summary
Severity: High
Advisory: CVE-2022-50668
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2022-50668
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.87, >=5.16.0 <6.0.18, >=6.1.0 <6.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix deadlock due to mbcache entry corruption

When manipulating xattr blocks, we can deadlock infinitely looping
inside ext4_xattr_block_set() where we constantly keep finding xattr
block for reuse in mbcache but we are unable to reuse it because its
reference count is too big. This happens because cache entry for the
xattr block is marked as reusable (e_reusable set) although its
reference count is too big. When this inconsistency happens, this
inconsistent state is kept indefinitely and so ext4_xattr_block_set()
keeps retrying indefinitely.

The inconsistent state is caused by non-atomic update of e_reusable bit.
e_reusable is part of a bitfield and e_reusable update can race with
update of e_referenced bit in the same bitfield resulting in loss of one
of the updates. Fix the problem by using atomic bitops instead.

This bug has been around for many years, but it became *much* easier
to hit after commit 65f8b80053a1 ("ext4: fix race when reusing xattr
blocks").

## References
- https://git.kernel.org/stable/c/127b80cefb941a81255c72f11081123f3a705369
- https://git.kernel.org/stable/c/1be16a0c2f10186df505e28b0cc92d7f3366e2a8
- https://git.kernel.org/stable/c/5bc0b2fda4b47c86278f7c6d30c211f425bf51cf
- https://git.kernel.org/stable/c/a44e84a9b7764c72896f7241a0ec9ac7e7ef38dd
- https://git.kernel.org/stable/c/af53065276376750dfac35a7248af18806404c5d
- https://git.kernel.org/stable/c/cc1538c693d25e282bed8c54b65c914a04023a78
- https://git.kernel.org/stable/c/efaa0ca678f56d47316a08030b2515678cebbc50
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50668.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50668
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
