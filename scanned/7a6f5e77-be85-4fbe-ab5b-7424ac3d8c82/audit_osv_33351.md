# [H] accel/qaic: Treat remaining == 0 as error in find_and_map_user_pages()

## Summary
Severity: High
Advisory: CVE-2025-40172
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40172
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.114, >=6.7.0 <6.12.55, >=6.13.0 <6.17.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/qaic: Treat remaining == 0 as error in find_and_map_user_pages()

Currently, if find_and_map_user_pages() takes a DMA xfer request from the
user with a length field set to 0, or in a rare case, the host receives
QAIC_TRANS_DMA_XFER_CONT from the device where resources->xferred_dma_size
is equal to the requested transaction size, the function will return 0
before allocating an sgt or setting the fields of the dma_xfer struct.
In that case, encode_addr_size_pairs() will try to access the sgt which
will lead to a general protection fault.

Return an EINVAL in case the user provides a zero-sized ALP, or the device
requests continuation after all of the bytes have been transferred.

## References
- https://git.kernel.org/stable/c/11f08c30a3e4157305ba692f1d44cca5fc9a8fca
- https://git.kernel.org/stable/c/1ab9733d14cc9987cc5dcd1f0ad1f416e302e2e6
- https://git.kernel.org/stable/c/48b1d42286bfef7628b1d6c8c28d4e456c90f725
- https://git.kernel.org/stable/c/551f1dfbcb7f3e6ed07f9d6c8c1c64337fcd0ede
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40172.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40172
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
