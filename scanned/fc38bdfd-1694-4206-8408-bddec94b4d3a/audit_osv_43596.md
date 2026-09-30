# [H] drm/vmwgfx: validate DRAW_PRIMITIVES header size before division

## Summary
Severity: High
Advisory: CVE-2026-74444
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74444
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.33 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: validate DRAW_PRIMITIVES header size before division

vmw_cmd_draw() computes

	maxnum = (header->size - sizeof(cmd->body)) / sizeof(*decl);

where header->size is u32 and is taken straight from the user-supplied
command stream.  When header->size is less than sizeof(cmd->body) the
unsigned subtraction wraps to nearly 4 GiB, producing a huge maxnum.
Any user-controlled cmd->body.numVertexDecls then passes the bound and
the loop dereferences decl[i] far past the end of the kernel command
bounce buffer, producing an out-of-bounds read of kernel memory.

Reject undersized headers up front.

## References
- https://git.kernel.org/stable/c/112c6ff29a56f3a22db4d5af869697aa07035ad6
- https://git.kernel.org/stable/c/2666cddf0dd218aa9bd1f99db688d1b532eac21a
- https://git.kernel.org/stable/c/85891d174707d8bddcec7a888fb4e1d17def34f3
- https://git.kernel.org/stable/c/b89ca4bba820f79dde52af15ee139fe6e8bbc314
- https://git.kernel.org/stable/c/bef30317fcb4c838a37bceb2fc76256eb6b975c1
- https://git.kernel.org/stable/c/c77cf8edae2bd3a1599115301cc7c98d0c78e731
- https://git.kernel.org/stable/c/dc0be7662b7b0ce28cb5eea864737793ed7b9e70
- https://git.kernel.org/stable/c/fc0c02f510e41650df3479f96e257acf87d8a20a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74444.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74444
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
