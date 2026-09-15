# [C] exfat: fix potential use-after-free in exfat_find_dir_entry()

## Summary
Severity: Critical
Advisory: CVE-2026-63808
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63808
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.260, >=5.11.0 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

exfat: fix potential use-after-free in exfat_find_dir_entry()

In exfat_find_dir_entry(), the buffer_head obtained from
exfat_get_dentry() is released with brelse(bh) before the fall-through
TYPE_EXTEND branch reads the directory entry through ep (which points
into bh->b_data):

	brelse(bh);
	if (entry_type == TYPE_EXTEND) {
		...
		len = exfat_extract_uni_name(ep, entry_uniname);
		...
	}

After brelse() drops our reference, nothing guarantees that the
underlying page backing bh->b_data remains valid for the subsequent
exfat_extract_uni_name() read. This is the same pattern fixed in
commit fc961522ddbd ("exfat: Fix potential use after free in
exfat_load_upcase_table()").

Move brelse(bh) so it runs after ep is no longer dereferenced on
each branch.

Confirmed on QEMU x86_64 with CONFIG_KASAN=y + CONFIG_DEBUG_PAGEALLOC=y
+ CONFIG_PAGE_POISONING=y on linux-next, using a crafted exFAT image
(long filename with same-hash collisions forcing the TYPE_EXTEND path).
With a debug-only invalidate_bdev() inserted between brelse(bh) and
the ep read to make the stale-deref window deterministic, the
unpatched kernel faults:

  BUG: KASAN: use-after-free in exfat_find_dir_entry+0x133b/0x15a0
  BUG: unable to handle page fault for address: ffff88801a5fa0c2
  Oops: 0000 [#1] SMP DEBUG_PAGEALLOC KASAN NOPTI
  RIP: 0010:exfat_find_dir_entry+0x1188/0x15a0

With this patch applied, the same instrumented harness completes
cleanly under the same sanitizer stack. I have not reproduced a
crash on an uninstrumented kernel under ordinary reclaim; the
instrumented A/B establishes the lifetime violation and that the
patch closes it, not an unaided triggerability claim.

## References
- https://git.kernel.org/stable/c/06c4e1e9967d332ac33ba38b7819851089ff9359
- https://git.kernel.org/stable/c/3f5f8ee9917cc2b9076ac533492d8a200edcabb8
- https://git.kernel.org/stable/c/4d101016d5e587f820b3ae2d5bb6770d86342649
- https://git.kernel.org/stable/c/708b97e792945d3e4653939fd3405d71a61ad065
- https://git.kernel.org/stable/c/8e0abc17fbd7e305802e84fe98b4950d50f9c433
- https://git.kernel.org/stable/c/adfacfbaeae2cb760f492357cc36b41f84ef7f86
- https://git.kernel.org/stable/c/e48f413c2815787b8cade2795e194e3c4cd782ef
- https://git.kernel.org/stable/c/e6f1a11cfb808441a43ffae9b476cc135732cd27
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63808.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63808
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
