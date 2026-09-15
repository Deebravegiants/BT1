# [H] Fix page corruption caused by racy check in __free_pages

## Summary
Severity: High
Advisory: CVE-2023-52739
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52739
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.168, >=5.11.0 <5.15.94, >=5.16.0 <6.1.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

Fix page corruption caused by racy check in __free_pages

When we upgraded our kernel, we started seeing some page corruption like
the following consistently:

  BUG: Bad page state in process ganesha.nfsd  pfn:1304ca
  page:0000000022261c55 refcount:0 mapcount:-128 mapping:0000000000000000 index:0x0 pfn:0x1304ca
  flags: 0x17ffffc0000000()
  raw: 0017ffffc0000000 ffff8a513ffd4c98 ffffeee24b35ec08 0000000000000000
  raw: 0000000000000000 0000000000000001 00000000ffffff7f 0000000000000000
  page dumped because: nonzero mapcount
  CPU: 0 PID: 15567 Comm: ganesha.nfsd Kdump: loaded Tainted: P    B      O      5.10.158-1.nutanix.20221209.el7.x86_64 #1
  Hardware name: VMware, Inc. VMware Virtual Platform/440BX Desktop Reference Platform, BIOS 6.00 04/05/2016
  Call Trace:
   dump_stack+0x74/0x96
   bad_page.cold+0x63/0x94
   check_new_page_bad+0x6d/0x80
   rmqueue+0x46e/0x970
   get_page_from_freelist+0xcb/0x3f0
   ? _cond_resched+0x19/0x40
   __alloc_pages_nodemask+0x164/0x300
   alloc_pages_current+0x87/0xf0
   skb_page_frag_refill+0x84/0x110
   ...

Sometimes, it would also show up as corruption in the free list pointer
and cause crashes.

After bisecting the issue, we found the issue started from commit
e320d3012d25 ("mm/page_alloc.c: fix freeing non-compound pages"):

	if (put_page_testzero(page))
		free_the_page(page, order);
	else if (!PageHead(page))
		while (order-- > 0)
			free_the_page(page + (1 << order), order);

So the problem is the check PageHead is racy because at this point we
already dropped our reference to the page.  So even if we came in with
compound page, the page can already be freed and PageHead can return
false and we will end up freeing all the tail pages causing double free.

## References
- https://git.kernel.org/stable/c/0a626e27f984dfbe96bd8e4fd08f20a2ede3ea23
- https://git.kernel.org/stable/c/3af734f3eac6f70ef8e272a80da40544b9d0f2b5
- https://git.kernel.org/stable/c/3b4c045a98f53a8890a94bb5846a390c8e39e673
- https://git.kernel.org/stable/c/462a8e08e0e6287e5ce13187257edbf24213ed03
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52739.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52739
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
