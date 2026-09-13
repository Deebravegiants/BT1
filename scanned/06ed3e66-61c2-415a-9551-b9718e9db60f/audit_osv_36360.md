# [H] ksmbd: add chann_lock to protect ksmbd_chann_list xarray

## Summary
Severity: High
Advisory: CVE-2026-23226
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2026-23226
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.12.77, >=6.13.0 <6.18.11, >=6.19.0 <6.19.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: add chann_lock to protect ksmbd_chann_list xarray

ksmbd_chann_list xarray lacks synchronization, allowing use-after-free in
multi-channel sessions (between lookup_chann_list() and ksmbd_chann_del).

Adds rw_semaphore chann_lock to struct ksmbd_session and protects
all xa_load/xa_store/xa_erase accesses.

## References
- https://git.kernel.org/stable/c/36ef605c0395b94b826a8c8d6f2697071173de6e
- https://git.kernel.org/stable/c/4c2ca31608521895dd742a43beca4b4d29762345
- https://git.kernel.org/stable/c/4f3a06cc57976cafa8c6f716646be6c79a99e485
- https://git.kernel.org/stable/c/e4a8a96a93d08570e0405cfd989a8a07e5b6ff33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23226.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23226
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
