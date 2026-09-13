# [H] xfrm: iptfs: only publish mode_data after clone setup

## Summary
Severity: High
Advisory: CVE-2026-31471
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31471
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: iptfs: only publish mode_data after clone setup

iptfs_clone_state() stores x->mode_data before allocating the reorder
window. If that allocation fails, the code frees the cloned state and
returns -ENOMEM, leaving x->mode_data pointing at freed memory.

The xfrm clone unwind later runs destroy_state() through x->mode_data,
so the failed clone path tears down IPTFS state that clone_state()
already freed.

Keep the cloned IPTFS state private until all allocations succeed so
failed clones leave x->mode_data unset. The destroy path already
handles a NULL mode_data pointer.

## References
- https://git.kernel.org/stable/c/371a43c4ac70cac0de9f9b1fc5b1660b9565b9f1
- https://git.kernel.org/stable/c/5784a1e2889c9525a8f036cb586930e232170bf7
- https://git.kernel.org/stable/c/d849a2f7309fc0616e79d13b008b0a47e0458b6e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31471.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31471
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
