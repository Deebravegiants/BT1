# [H] net: decrease cached dst counters in dst_release

## Summary
Severity: High
Advisory: CVE-2025-22057
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22057
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: decrease cached dst counters in dst_release

Upstream fix ac888d58869b ("net: do not delay dst_entries_add() in
dst_release()") moved decrementing the dst count from dst_destroy to
dst_release to avoid accessing already freed data in case of netns
dismantle. However in case CONFIG_DST_CACHE is enabled and OvS+tunnels
are used, this fix is incomplete as the same issue will be seen for
cached dsts:

  Unable to handle kernel paging request at virtual address ffff5aabf6b5c000
  Call trace:
   percpu_counter_add_batch+0x3c/0x160 (P)
   dst_release+0xec/0x108
   dst_cache_destroy+0x68/0xd8
   dst_destroy+0x13c/0x168
   dst_destroy_rcu+0x1c/0xb0
   rcu_do_batch+0x18c/0x7d0
   rcu_core+0x174/0x378
   rcu_core_si+0x18/0x30

Fix this by invalidating the cache, and thus decrementing cached dst
counters, in dst_release too.

## References
- https://git.kernel.org/stable/c/3a0a3ff6593d670af2451ec363ccb7b18aec0c0a
- https://git.kernel.org/stable/c/836415a8405c9665ae55352fc5ba865c242f5e4f
- https://git.kernel.org/stable/c/92a5c18513117be69bc00419dd1724c1940f8fcd
- https://git.kernel.org/stable/c/ccc331fd5bcae131d2627d5ef099d4a1f6540aea
- https://git.kernel.org/stable/c/e833e7ad64eb2f63867f65303be49ca30ee8819e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22057.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22057
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
