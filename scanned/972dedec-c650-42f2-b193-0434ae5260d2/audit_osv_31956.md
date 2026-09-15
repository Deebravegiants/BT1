# [H] exfat: fix random stack corruption after get_block

## Summary
Severity: High
Advisory: CVE-2025-22036
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22036
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

exfat: fix random stack corruption after get_block

When get_block is called with a buffer_head allocated on the stack, such
as do_mpage_readpage, stack corruption due to buffer_head UAF may occur in
the following race condition situation.

     <CPU 0>                      <CPU 1>
mpage_read_folio
  <<bh on stack>>
  do_mpage_readpage
    exfat_get_block
      bh_read
        __bh_read
	  get_bh(bh)
          submit_bh
          wait_on_buffer
                              ...
                              end_buffer_read_sync
                                __end_buffer_read_notouch
                                   unlock_buffer
          <<keep going>>
        ...
      ...
    ...
  ...
<<bh is not valid out of mpage_read_folio>>
   .
   .
another_function
  <<variable A on stack>>
                                   put_bh(bh)
                                     atomic_dec(bh->b_count)
  * stack corruption here *

This patch returns -EAGAIN if a folio does not have buffers when bh_read
needs to be called. By doing this, the caller can fallback to functions
like block_read_full_folio(), create a buffer_head in the folio, and then
call get_block again.

Let's do not call bh_read() with on-stack buffer_head.

## References
- https://git.kernel.org/stable/c/1bb7ff4204b6d4927e982cd256286c09ed4fd8ca
- https://git.kernel.org/stable/c/49b0a6ab8e528a0c1c50e37cef9b9c7c121365f2
- https://git.kernel.org/stable/c/f7447286363dc1e410bf30b87d75168f3519f9cc
- https://git.kernel.org/stable/c/f807a6bf2005740fa26b4f59c4a003dc966b9afd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22036.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22036
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
