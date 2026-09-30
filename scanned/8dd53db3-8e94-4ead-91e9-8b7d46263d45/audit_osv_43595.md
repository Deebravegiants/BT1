# [H] drm/vmwgfx: bound DMA command body size against suffix pointer

## Summary
Severity: High
Advisory: CVE-2026-74443
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74443
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.33 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: bound DMA command body size against suffix pointer

vmw_cmd_dma() locates the DMA suffix at

	(unsigned long) &cmd->body + header->size - sizeof(*suffix)

without checking that header->size is large enough to contain both
cmd->body and the suffix.  An undersized header makes the suffix
pointer underflow back into the previous command in the bounce
buffer.  The verifier later writes suffix->maximumOffset, clobbering
verified fields of an already-relocated earlier command -- a TOCTOU
on the device-visible command stream that lets one command rewrite
another's GMR id, surface id, or other authenticated fields.

Reject the command if the body is too small for the suffix to fit.

## References
- https://git.kernel.org/stable/c/036e16ada95389bdc30f41068af04c1d0872fad0
- https://git.kernel.org/stable/c/7e40e6120fb232a10b543ffd994e5c6d8f3a2cc6
- https://git.kernel.org/stable/c/9759da60e38d7b9db44dc92713e4e0391883d221
- https://git.kernel.org/stable/c/a4a37080a5ac777b59306cfcdf854cc05d7604d4
- https://git.kernel.org/stable/c/d5d7ada4e1296b00d89fe82b2ca850cc7809d6f7
- https://git.kernel.org/stable/c/eb20f418933bea53375843b27b4022c1810be63b
- https://git.kernel.org/stable/c/f4f1db96bfd68b81053693ba53405b6f510ac16c
- https://git.kernel.org/stable/c/fcd1e56e7816b31a1050ccc67df722b20f6bb15d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74443.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74443
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
