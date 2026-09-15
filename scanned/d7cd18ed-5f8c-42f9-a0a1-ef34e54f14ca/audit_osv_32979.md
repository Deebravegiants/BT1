# [C] netfilter: nf_conntrack: fix crash due to removal of uninitialised entry

## Summary
Severity: Critical
Advisory: CVE-2025-38472
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-28
Source: https://osv.dev/vulnerability/CVE-2025-38472
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.147, >=6.2.0 <6.6.100, >=6.7.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conntrack: fix crash due to removal of uninitialised entry

A crash in conntrack was reported while trying to unlink the conntrack
entry from the hash bucket list:
    [exception RIP: __nf_ct_delete_from_lists+172]
    [..]
 #7 [ff539b5a2b043aa0] nf_ct_delete at ffffffffc124d421 [nf_conntrack]
 #8 [ff539b5a2b043ad0] nf_ct_gc_expired at ffffffffc124d999 [nf_conntrack]
 #9 [ff539b5a2b043ae0] __nf_conntrack_find_get at ffffffffc124efbc [nf_conntrack]
    [..]

The nf_conn struct is marked as allocated from slab but appears to be in
a partially initialised state:

 ct hlist pointer is garbage; looks like the ct hash value
 (hence crash).
 ct->status is equal to IPS_CONFIRMED|IPS_DYING, which is expected
 ct->timeout is 30000 (=30s), which is unexpected.

Everything else looks like normal udp conntrack entry.  If we ignore
ct->status and pretend its 0, the entry matches those that are newly
allocated but not yet inserted into the hash:
  - ct hlist pointers are overloaded and store/cache the raw tuple hash
  - ct->timeout matches the relative time expected for a new udp flow
    rather than the absolute 'jiffies' value.

If it were not for the presence of IPS_CONFIRMED,
__nf_conntrack_find_get() would have skipped the entry.

Theory is that we did hit following race:

cpu x 			cpu y			cpu z
 found entry E		found entry E
 E is expired		<preemption>
 nf_ct_delete()
 return E to rcu slab
					init_conntrack
					E is re-inited,
					ct->status set to 0
					reply tuplehash hnnode.pprev
					stores hash value.

cpu y found E right before it was deleted on cpu x.
E is now re-inited on cpu z.  cpu y was preempted before
checking for expiry and/or confirm bit.

					->refcnt set to 1
					E now owned by skb
					->timeout set to 30000

If cpu y were to resume now, it would observe E as
expired but would skip E due to missing CONFIRMED bit.

					nf_conntrack_confirm gets called
					sets: ct->status |= CONFIRMED
					This is wrong: E is not yet added
					to hashtable.

cpu y resumes, it observes E as expired but CONFIRMED:
			<resumes>
			nf_ct_expired()
			 -> yes (ct->timeout is 30s)
			confirmed bit set.

cpu y will try to delete E from the hashtable:
			nf_ct_delete() -> set DYING bit
			__nf_ct_delete_from_lists

Even this scenario doesn't guarantee a crash:
cpu z still holds the table bucket lock(s) so y blocks:

			wait for spinlock held by z

					CONFIRMED is set but there is no
					guarantee ct will be added to hash:
					"chaintoolong" or "clash resolution"
					logic both skip the insert step.
					reply hnnode.pprev still stores the
					hash value.

					unlocks spinlock
					return NF_DROP
			<unblocks, then
			 crashes on hlist_nulls_del_rcu pprev>

In case CPU z does insert the entry into the hashtable, cpu y will unlink
E again right away but no crash occurs.

Without 'cpu y' race, 'garbage' hlist is of no consequence:
ct refcnt remains at 1, eventually skb will be free'd and E gets
destroyed via: nf_conntrack_put -> nf_conntrack_destroy -> nf_ct_destroy.

To resolve this, move the IPS_CONFIRMED assignment after the table
insertion but before the unlock.

Pablo points out that the confirm-bit-store could be reordered to happen
before hlist add resp. the timeout fixup, so switch to set_bit and
before_atomic memory barrier to prevent this.

It doesn't matter if other CPUs can observe a newly inserted entry right
before the CONFIRMED bit was set:

Such event cannot be distinguished from above "E is the old incarnation"
case: the entry will be skipped.

Also change nf_ct_should_gc() to first check the confirmed bit.

The gc sequence is:
 1. Check if entry has expired, if not skip to next entry
 2. Obtain a reference to the expired entry.
 3. Call nf_ct_should_gc() to double-check step 1.

nf_ct_should_gc() is thus called only for entries that already failed an
expiry check. After this patch, once the confirmed bit check pas
---truncated---

## References
- https://git.kernel.org/stable/c/2d72afb340657f03f7261e9243b44457a9228ac7
- https://git.kernel.org/stable/c/76179961c423cd698080b5e4d5583cf7f4fcdde9
- https://git.kernel.org/stable/c/938ce0e8422d3793fe30df2ed0e37f6bc0598379
- https://git.kernel.org/stable/c/a47ef874189d47f934d0809ae738886307c0ea22
- https://git.kernel.org/stable/c/fc38c249c622ff5e3011b8845fd49dbfd9289afc
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38472.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38472
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
