# [C] smb: client: avoid double-free in smbd_free_send_io() after smbd_send_batch_flush()

## Summary
Severity: Critical
Advisory: CVE-2026-31609
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31609
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: avoid double-free in smbd_free_send_io() after smbd_send_batch_flush()

smbd_send_batch_flush() already calls smbd_free_send_io(),
so we should not call it again after smbd_post_send()
moved it to the batch list.

## References
- https://git.kernel.org/stable/c/22b7c1c619d808aec4cad3dc42103345e370d107
- https://git.kernel.org/stable/c/27b7c3e916218b5eb2ee350211140e961bfc49be
- https://git.kernel.org/stable/c/a9940dcbe5cb92482c04efc7341039ddf7dbf607
- https://git.kernel.org/stable/c/f9a162c2bbcd0ac85bd07c5b37cf20286048b65c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31609.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31609
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
