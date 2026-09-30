# [H] misc: fastrpc: Fix double free of 'buf' in error path

## Summary
Severity: High
Advisory: CVE-2024-46741
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46741
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: fastrpc: Fix double free of 'buf' in error path

smatch warning:
drivers/misc/fastrpc.c:1926 fastrpc_req_mmap() error: double free of 'buf'

In fastrpc_req_mmap() error path, the fastrpc buffer is freed in
fastrpc_req_munmap_impl() if unmap is successful.

But in the end, there is an unconditional call to fastrpc_buf_free().
So the above case triggers the double free of fastrpc buf.

## References
- https://git.kernel.org/stable/c/4753cc37b6606ef9a7ec22861d380d45e2707f9a
- https://git.kernel.org/stable/c/bfc1704d909dc9911a558b1a5833d3d61a43a1f2
- https://git.kernel.org/stable/c/e8c276d4dc0e19ee48385f74426aebc855b49aaf
- https://git.kernel.org/stable/c/f77dc8a75859e559f3238a6d906206259227985e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46741.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46741
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
