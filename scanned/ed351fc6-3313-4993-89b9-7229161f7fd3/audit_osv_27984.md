# [H] netfilter: nft_set_pipapo: do not free live element

## Summary
Severity: High
Advisory: CVE-2024-26924
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-24
Source: https://osv.dev/vulnerability/CVE-2024-26924
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.216, >=5.11.0 <5.15.157, >=5.16.0 <6.1.88, >=6.2.0 <6.6.29, >=6.7.0 <6.8.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_set_pipapo: do not free live element

Pablo reports a crash with large batches of elements with a
back-to-back add/remove pattern.  Quoting Pablo:

  add_elem("00000000") timeout 100 ms
  ...
  add_elem("0000000X") timeout 100 ms
  del_elem("0000000X") <---------------- delete one that was just added
  ...
  add_elem("00005000") timeout 100 ms

  1) nft_pipapo_remove() removes element 0000000X
  Then, KASAN shows a splat.

Looking at the remove function there is a chance that we will drop a
rule that maps to a non-deactivated element.

Removal happens in two steps, first we do a lookup for key k and return the
to-be-removed element and mark it as inactive in the next generation.
Then, in a second step, the element gets removed from the set/map.

The _remove function does not work correctly if we have more than one
element that share the same key.

This can happen if we insert an element into a set when the set already
holds an element with same key, but the element mapping to the existing
key has timed out or is not active in the next generation.

In such case its possible that removal will unmap the wrong element.
If this happens, we will leak the non-deactivated element, it becomes
unreachable.

The element that got deactivated (and will be freed later) will
remain reachable in the set data structure, this can result in
a crash when such an element is retrieved during lookup (stale
pointer).

Add a check that the fully matching key does in fact map to the element
that we have marked as inactive in the deactivation step.
If not, we need to continue searching.

Add a bug/warn trap at the end of the function as well, the remove
function must not ever be called with an invisible/unreachable/non-existent
element.

v2: avoid uneeded temporary variable (Stefano)

## References
- https://git.kernel.org/stable/c/14b001ba221136c15f894577253e8db535b99487
- https://git.kernel.org/stable/c/3cfc9ec039af60dbd8965ae085b2c2ccdcfbe1cc
- https://git.kernel.org/stable/c/41d8fdf3afaff312e17466e4ab732937738d5644
- https://git.kernel.org/stable/c/7a1679e2d9bfa3b5f8755c2c7113e54b7d42bd46
- https://git.kernel.org/stable/c/e3b887a9c11caf8357a821260e095f2a694a34f2
- https://git.kernel.org/stable/c/ebf7c9746f073035ee26209e38c3a1170f7b349a
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4EZ6PJW7VOZ224TD7N4JZNU6KV32ZJ53/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DAMSOZXJEPUOXW33WZYWCVAY7Z5S7OOY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GCBZZEC7L7KTWWAS2NLJK6SO3IZIL4WW/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26924.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26924
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
