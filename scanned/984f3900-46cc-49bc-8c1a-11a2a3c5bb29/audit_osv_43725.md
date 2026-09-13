# [H] ipv6: prevent in6_dev_get() from resurrecting inet6_dev

## Summary
Severity: High
Advisory: CVE-2026-74630
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74630
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.19 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: prevent in6_dev_get() from resurrecting inet6_dev

in6_dev_get() reads dev->ip6_ptr under RCU and then unconditionally
increments its refcount. Device teardown can clear the pointer and drop
the last reference between these operations. The increment then
resurrects an object whose RCU free has already been queued, so callers
can use it after it is freed.

Use refcount_inc_not_zero() and return NULL when the object has already
reached zero. RCU keeps the memory accessible through the attempted
reference acquisition, and a successful increment pins the object for
the caller.

An independent run on the exact unpatched 6f5156d7a31a (v7.2-rc3)
kernel reproduced the invalid reference acquisition as UID 1000:

  refcount_t: addition on 0; use-after-free.
  ip6_mc_source+0xef4/0x17e0

It was followed by the corresponding reference underflow in
ip6_mc_source(). The supplied trace from the same unpatched revision
additionally shows the access after the RCU read-side section ends:

  BUG: KASAN: slab-use-after-free in mutex_lock+0x76/0xe0
  Write of size 8 at addr ffff888015b50240 by task poc/1219

Bug found and triaged by OpenAI Security Research and
validated by Trail of Bits.

## References
- https://git.kernel.org/stable/c/0e243671bc7b8eaf00f83dd2f4367436dc0cff98
- https://git.kernel.org/stable/c/145812b678de9f3b59780173be3c0d22ed60dd93
- https://git.kernel.org/stable/c/14e812ab41df0cac033479da835ec9a5de633404
- https://git.kernel.org/stable/c/1c206d461c680c3151daa3c89fc26eaf5bf98a7f
- https://git.kernel.org/stable/c/680fbd7942185448eadb990a3d10a53eb946b702
- https://git.kernel.org/stable/c/785d908f8d21c8bc78b6fb2c2932ab662bf6918a
- https://git.kernel.org/stable/c/aedcfefdb5b7ed7f8a6196a3e68a25bdbe51d2f8
- https://git.kernel.org/stable/c/cc5bd568f9b7683e60841b6fd02c10d64535bd6e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74630.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74630
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
