# [H] misc: fastrpc: possible double-free of cctx->remote_heap

## Summary
Severity: High
Advisory: CVE-2026-31730
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31730
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: fastrpc: possible double-free of cctx->remote_heap

fastrpc_init_create_static_process() may free cctx->remote_heap on the
err_map path but does not clear the pointer. Later, fastrpc_rpmsg_remove()
frees cctx->remote_heap again if it is non-NULL, which can lead to a
double-free if the INIT_CREATE_STATIC ioctl hits the error path and the rpmsg
device is subsequently removed/unbound.
Clear cctx->remote_heap after freeing it in the error path to prevent the
later cleanup from freeing it again.

This issue was found by an in-house analysis workflow that extracts AST-based
information and runs static checks, with LLM assistance for triage, and was
confirmed by manual code review.
No hardware testing was performed.

## References
- https://git.kernel.org/stable/c/0bdee4118340c5a756220c1b29a7dab86bb0aa65
- https://git.kernel.org/stable/c/3a164f640953cc982804746e772d379171aff5c6
- https://git.kernel.org/stable/c/4b8e527aca357a6488680713bd88007cf8f547fe
- https://git.kernel.org/stable/c/ba2c83167b215da30fa2aae56b140198cf8d8408
- https://git.kernel.org/stable/c/f67d368d26764a357691b2b3a33d3cb55b435bfc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31730.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31730
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
