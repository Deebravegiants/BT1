# [H] misc: fastrpc: Remove buffer from list prior to unmap operation

## Summary
Severity: High
Advisory: CVE-2026-74647
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74647
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.267, >=5.11.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: fastrpc: Remove buffer from list prior to unmap operation

fastrpc_req_munmap_impl() is called to unmap any buffer. The buffer is
getting removed from the list after it is unmapped from DSP. This can
create potential race conditions if multiple threads invoke unmap
concurrently, where one thread may remove the entry from the list while
another thread's unmap operation is still ongoing.

Fix this by removing the buffer entry from the list before calling the
unmap operation. If the unmap fails, the entry is re-added to the list
so that userspace can retry the unmap, or alternatively, the buffer
will be cleaned up during device release when the DSP process is torn
down and all DSP-side mappings are freed along with remaining buffers
in the list.

## References
- https://git.kernel.org/stable/c/0beaa9bd7eb10d9b5e6352ed5161f3f3bbd4c3c5
- https://git.kernel.org/stable/c/1edb654b2b41baee2ab5cf418baaf6e57dfbd802
- https://git.kernel.org/stable/c/4716c23c206a2f99ca54ebfdd8b5ba9dd0102240
- https://git.kernel.org/stable/c/6102ceb4eab845743ee57acd3863fbd06e93c927
- https://git.kernel.org/stable/c/97273624f7b356eaf8261609a75cfcb8738a165a
- https://git.kernel.org/stable/c/99f8de36c84cb9b872157aa6c3578c2480cee4b8
- https://git.kernel.org/stable/c/9bf22a7d950cec2d1efeca7f16bb20fcca84c36a
- https://git.kernel.org/stable/c/fe70329055977fc1e8dc6291318d0dd75470795a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74647.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74647
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
