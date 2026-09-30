# [H] ASoC: SOF: ipc3-control: Fix heap overflow in bytes_ext put/get

## Summary
Severity: High
Advisory: CVE-2026-72262
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72262
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.184, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: SOF: ipc3-control: Fix heap overflow in bytes_ext put/get

The ipc_control_data buffer is allocated as kzalloc(max_size), where
max_size covers the entire struct sof_ipc_ctrl_data including its
flexible array payload. However, the bounds checks in bytes_ext_put
and _bytes_ext_get compared user data lengths against max_size
directly, ignoring that cdata->data sits at an offset of
sizeof(struct sof_ipc_ctrl_data) bytes into the allocation.

This allowed writing up to sizeof(struct sof_ipc_ctrl_data) bytes past
the end of the heap buffer from unprivileged userspace via the ALSA TLV
kcontrol interface, and similarly allowed over-reading adjacent heap
data on the get path.

Fix all bounds checks to subtract sizeof(*cdata) from max_size so they
reflect the actual space available at the cdata->data offset. Also fix
the error-path restore in bytes_ext_put which wrote to cdata->data
instead of cdata, causing the same overflow.

## References
- https://git.kernel.org/stable/c/121577383b5cf221e86581e0f2bcca4c66f17469
- https://git.kernel.org/stable/c/1adde1941bba7b0d7104b86ed819d48d81cb0ad9
- https://git.kernel.org/stable/c/af4b437a463ac0482ba705434a44da06783778e6
- https://git.kernel.org/stable/c/eaa67e139c9217099e2a7b717aeeb46c65de3494
- https://git.kernel.org/stable/c/f4933e1d11b97b6a0951648b7c3e53850e1b33a9
- https://git.kernel.org/stable/c/fd46668d538993218eea19c6925c868ac0f2630c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72262.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72262
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
