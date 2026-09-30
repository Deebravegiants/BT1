# [H] bpf: fix UAF by restoring RCU-delayed inode freeing in bpffs

## Summary
Severity: High
Advisory: CVE-2026-74363
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74363
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.18.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: fix UAF by restoring RCU-delayed inode freeing in bpffs

commit 4f375ade6aa9 ("bpf: Avoid RCU context warning when unpinning
htab with internal structs") moved inode cleanup from ->free_inode()
into ->destroy_inode() to avoid sleeping in RCU context when calling
bpf_any_put(). However this removed the RCU delay on freeing the
inode itself and the cached symlink body (i_link), both of which
can be accessed by RCU pathwalk (pick_link, may_lookup etc.).

This causes a use-after-free when a concurrent unlinkat() drops the
last inode reference and destroy_inode() frees the inode immediately,
while another task is still walking the path in RCU mode and reads
inode->i_opflags (offset +2) inside current_time() -> is_mgtime().

KASAN reports:
  BUG: KASAN: slab-use-after-free in is_mgtime include/linux/fs.h:2313
  Read of size 2 at addr ffff8880407e4282 (offset +2 = i_opflags)

The rules (per Al Viro):
  ->destroy_inode()  called immediately, can sleep, use for blocking
                     cleanup e.g. bpf_any_put()
  ->free_inode()     called after RCU grace period, use for freeing
                     inode and anything RCU-accessible e.g. i_link

Fix: split the two concerns properly:
  - keep bpf_any_put() in bpf_destroy_inode() since it is blocking
    and needs to run promptly
  - introduce bpf_free_inode() to handle kfree(i_link) and
    free_inode_nonrcu() with proper RCU delay, preventing the UAF

## References
- https://git.kernel.org/stable/c/0497ff765746d9b2d17445c8f7cc737b36c0152a
- https://git.kernel.org/stable/c/53649846e0437d1d9b7cb993cfe54c367addf7ae
- https://git.kernel.org/stable/c/5fecb71c10c28aef276ba49c718dc961745fdcf0
- https://git.kernel.org/stable/c/61f19729728243c82476dee31315143ed3275e7f
- https://git.kernel.org/stable/c/b93c55b4932dd7e32dca8cf34a3443cc87a02906
- https://git.kernel.org/stable/c/c70d0f9114c3cc156f6029a400c4eb7e6f7c82b2
- https://git.kernel.org/stable/c/ea1c243c39e32b7fc1c2edfe32081ff7e30a877c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74363.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74363
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
