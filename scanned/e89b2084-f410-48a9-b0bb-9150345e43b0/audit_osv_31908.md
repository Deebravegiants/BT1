# [H] ksmbd: fix use-after-free in ksmbd_free_work_struct

## Summary
Severity: High
Advisory: CVE-2025-21967
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21967
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.84, >=6.7.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free in ksmbd_free_work_struct

->interim_entry of ksmbd_work could be deleted after oplock is freed.
We don't need to manage it with linked list. The interim request could be
immediately sent whenever a oplock break wait is needed.

## References
- https://git.kernel.org/stable/c/62746ae3f5414244a96293e3b017be637b641280
- https://git.kernel.org/stable/c/bb39ed47065455604729404729d9116868638d31
- https://git.kernel.org/stable/c/eb51f6f59d19b92f6fe84d3873f958495ab32f0a
- https://git.kernel.org/stable/c/fb776765bfc21d5e4ed03bb3d4406c2b86ff1ac3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21967.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21967
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
