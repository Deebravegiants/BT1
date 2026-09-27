# [H] btrfs: reinitialize delayed ref list after deleting it from the list

## Summary
Severity: High
Advisory: CVE-2024-50273
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50273
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: reinitialize delayed ref list after deleting it from the list

At insert_delayed_ref() if we need to update the action of an existing
ref to BTRFS_DROP_DELAYED_REF, we delete the ref from its ref head's
ref_add_list using list_del(), which leaves the ref's add_list member
not reinitialized, as list_del() sets the next and prev members of the
list to LIST_POISON1 and LIST_POISON2, respectively.

If later we end up calling drop_delayed_ref() against the ref, which can
happen during merging or when destroying delayed refs due to a transaction
abort, we can trigger a crash since at drop_delayed_ref() we call
list_empty() against the ref's add_list, which returns false since
the list was not reinitialized after the list_del() and as a consequence
we call list_del() again at drop_delayed_ref(). This results in an
invalid list access since the next and prev members are set to poison
pointers, resulting in a splat if CONFIG_LIST_HARDENED and
CONFIG_DEBUG_LIST are set or invalid poison pointer dereferences
otherwise.

So fix this by deleting from the list with list_del_init() instead.

## References
- https://git.kernel.org/stable/c/2cb1a73d1d44a1c11b0ee5eeced765dd80ec48e6
- https://git.kernel.org/stable/c/2fd0948a483e9cb2d669c7199bc620a21c97673d
- https://git.kernel.org/stable/c/50a3933760b427759afdd23156a7280a19357a92
- https://git.kernel.org/stable/c/93c5b8decc0ef39ba84f4211d2db6da0a4aefbeb
- https://git.kernel.org/stable/c/bf0b0c6d159767c0d1c21f793950d78486690ee0
- https://git.kernel.org/stable/c/c24fa427fc0ae827b2a3a07f13738cbf82c3f851
- https://git.kernel.org/stable/c/c9a75ec45f1111ef530ab186c2a7684d0a0c9245
- https://git.kernel.org/stable/c/f04be6d68f715c1473a8422fc0460f57b5e99931
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50273.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50273
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
