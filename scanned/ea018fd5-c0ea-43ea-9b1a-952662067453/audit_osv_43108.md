# [H] fs/ntfs3: resize log->one_page_buf when adopting on-disk page size

## Summary
Severity: High
Advisory: CVE-2026-72470
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72470
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: resize log->one_page_buf when adopting on-disk page size

log_replay() allocates log->one_page_buf using the page size that was
chosen from the host PAGE_SIZE:

	log->one_page_buf = kmalloc(log->page_size, GFP_NOFS);

Later, when a restart area is found, the log page size recorded on disk
is adopted:

	t32 = le32_to_cpu(log->rst_info.r_page->sys_page_size);
	if (log->page_size != t32) {
		log->l_size = log->orig_file_size;
		log->page_size = norm_file_page(t32, &log->l_size,
						t32 == DefaultLogPageSize);
	}

If the on-disk page size is larger than the size used for the initial
allocation, log->page_size grows but one_page_buf is left at its
original, smaller size. A subsequent unaligned read_log_page() then
reads log->page_size bytes into the undersized scratch buffer:

	page_buf = page_off ? log->one_page_buf : *buffer;
	err = ntfs_read_run_nb_ra(ni->mi.sbi, &ni->file.run, page_vbo, page_buf,
				  log->page_size, NULL, &log->read_ahead);

overflowing the allocation. This is reachable when mounting a dirty
NTFS volume whose log was formatted with a page size larger than the
buffer initially allocated on the mounting host (for example a 64K-log
volume mounted on a host that allocated a 4K scratch buffer).

Grow one_page_buf when the adopted on-disk page size exceeds the size
used for the initial allocation. On krealloc() failure the original
buffer is left intact and freed by the existing error path.

## References
- https://git.kernel.org/stable/c/2097a2537d9d1c29c0e20ed0dbf717a0ccd8f374
- https://git.kernel.org/stable/c/4f129fc6f756f8541e5bff45b1804cc11b1ec712
- https://git.kernel.org/stable/c/5a35454179fe1041d9cd286f5d320ce0d448c12a
- https://git.kernel.org/stable/c/c99444f6dfca893f6d310aae4a53c620f98f7b4f
- https://git.kernel.org/stable/c/f1422df595d69b997d23a8f11e12c528ccef7fad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72470.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72470
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
