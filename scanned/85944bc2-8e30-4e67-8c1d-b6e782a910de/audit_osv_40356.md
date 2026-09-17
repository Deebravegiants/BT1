# [H] um: Fix potential race condition in TLB sync

## Summary
Severity: High
Advisory: CVE-2026-53020
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53020
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

um: Fix potential race condition in TLB sync

During the TLB sync, we need to traverse and modify the page table,
so we should hold the page table lock. Since full SMP support for
threads within the same process is still missing, let's disable the
split page table lock for simplicity.

## References
- https://git.kernel.org/stable/c/102331b66bcaf1f41f50b9c4cd5c36e46bafa9f3
- https://git.kernel.org/stable/c/f21c343ec7419377bff89ab11146c03ae117036f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53020.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53020
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
