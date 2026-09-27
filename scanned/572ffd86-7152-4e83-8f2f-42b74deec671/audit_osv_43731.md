# [H] ALSA: usx2y: bound the hwdep mmap fault offset

## Summary
Severity: High
Advisory: CVE-2026-74641
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74641
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.266, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: usx2y: bound the hwdep mmap fault offset

snd_us428ctls_vm_fault() turns the faulting page offset into a kernel
address with no bound of any kind:

	offset = vmf->pgoff << PAGE_SHIFT;
	vaddr = (char *)(...)->us428ctls_sharedmem + offset;
	page = virt_to_page(vaddr);
	get_page(page);
	vmf->page = page;

	return 0;

snd_us428ctls_mmap() checks only the length of the mapping, never the
offset, and us428ctls_sharedmem is a single page from
alloc_pages_exact().  For a character device file_mmap_size_max()
returns ULONG_MAX, so the mm layer imposes no ceiling either.  Every page
offset above zero resolves to a struct page outside the object, and the
handler installs it into the caller's address space read-write; the vma
is not marked read-only.

The caller picks the page frame with a single mmap() argument and gets
read-write access to a page of kernel memory it does not own; an offset
that lands in an unpopulated vmemmap region oopses instead.

A process that can open the hwdep node of an attached US-X2Y reaches
this after loading the FPGA image through the same node; no capability
check is involved.

On 7.2.0-rc5 (arm64), mmap() with a large offset:

  Unable to handle kernel paging request at virtual address fffffdffc45d5ac8
  pc : snd_us428ctls_vm_fault+0x68/0x140 [snd_usb_usx2y]
  Call trace:
   snd_us428ctls_vm_fault+0x68/0x140 [snd_usb_usx2y]
   __do_fault
   __handle_mm_fault
   handle_mm_fault
   el0_da

Reject any offset outside the shared region.  The pcm hwdep handler in
usx2yhwdeppcm.c computes its address the same way and needs the same
bound.

Discovered by XBOW, triaged by Baul Lee <baul.lee@xbow.com>

## References
- https://git.kernel.org/stable/c/10a87401fb3148c388e55df0148295b3b137da07
- https://git.kernel.org/stable/c/2ca1eea3cd17930daffe9e429a7c89232036ec24
- https://git.kernel.org/stable/c/34ab56ed854baa73a731cfd99af689f0b1bac444
- https://git.kernel.org/stable/c/4208db2453e1ea71b8048a5b7802360cb29a53f1
- https://git.kernel.org/stable/c/5bf5ccddf00b59f1e3ea7e65d76a5f5b5c21cc2e
- https://git.kernel.org/stable/c/ad6fedea65c6e90eda00d716c8bf20cdc437ed10
- https://git.kernel.org/stable/c/f613b4a2d87247b51a1b2b330f2e083a454125f2
- https://git.kernel.org/stable/c/f75d6f61f0d9c5c1ea725104014e10d26d1e3a00
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74641.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74641
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
