# [C] nvmet-rdma: handle inline data with a nonzero offset

## Summary
Severity: Critical
Advisory: CVE-2026-72129
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72129
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet-rdma: handle inline data with a nonzero offset

nvmet_rdma_use_inline_sg() maps the host-controlled inline data offset
into the per-command inline scatterlist.  The bounds check admits any
offset with off + len <= inline_data_size, but the mapping still assumes
the data begins in the first inline page:

	sg->offset = off;
	sg->length = min_t(int, len, PAGE_SIZE - off);

When a port is configured with inline_data_size > PAGE_SIZE (settable up
to max(SZ_16K, PAGE_SIZE)), an offset in (PAGE_SIZE, inline_data_size]
makes "PAGE_SIZE - off" underflow, so sg->length is set to ~4 GiB and
the block backend reads far past the first inline page.  num_pages(len)
also ignores the offset, so an in-bounds offset whose [off, off+len)
span crosses a page boundary under-counts the scatterlist.

Map the offset properly: split it into a page index and an in-page
offset, start the scatterlist at that page, and size the page count from
page_off + len.  Because the request scatterlist may now start at
inline_sg[page_idx] rather than inline_sg[0], generalize the inline-SGL
identity test in nvmet_rdma_release_rsp() to a range test; otherwise the
persistent inline scatterlist is mistaken for an allocated one and
nvmet_req_free_sgls() frees an inline page (and warns in
free_large_kmalloc()).

## References
- https://git.kernel.org/stable/c/11401371152b228448a41d79c6de1c938f93049a
- https://git.kernel.org/stable/c/2944113ad5fbcdf5d349d857c03d2a44b6de75b8
- https://git.kernel.org/stable/c/42a8ea3acd883f4f210d9e54e0975b1e2292b529
- https://git.kernel.org/stable/c/48c0162f647bb47e6084ffbc71b8f213f5e2f4f8
- https://git.kernel.org/stable/c/7c96581169c9d9a7d0726e554313acfbead6141c
- https://git.kernel.org/stable/c/98bcdfa619150b2f41fa15bac140dbaf2584ad05
- https://git.kernel.org/stable/c/bf8bcc1c137d54a62a428b00051fdbb13660673b
- https://git.kernel.org/stable/c/c2106ba1b14d644a5203bea1a50dbe25dcad713c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72129.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72129
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
