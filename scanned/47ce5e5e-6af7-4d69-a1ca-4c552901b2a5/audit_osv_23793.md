# [M] nvme-pci: fix a NULL pointer dereference in nvme_alloc_admin_tags

## Summary
Severity: Medium
Advisory: CVE-2022-49492
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49492
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-pci: fix a NULL pointer dereference in nvme_alloc_admin_tags

In nvme_alloc_admin_tags, the admin_q can be set to an error (typically
-ENOMEM) if the blk_mq_init_queue call fails to set up the queue, which
is checked immediately after the call. However, when we return the error
message up the stack, to nvme_reset_work the error takes us to
nvme_remove_dead_ctrl()
  nvme_dev_disable()
   nvme_suspend_queue(&dev->queues[0]).

Here, we only check that the admin_q is non-NULL, rather than not
an error or NULL, and begin quiescing a queue that never existed, leading
to bad / NULL pointer dereference.

## References
- https://git.kernel.org/stable/c/54a4c1e47d1b2585e74920399455bd9abbfb2bd7
- https://git.kernel.org/stable/c/7a28556082d1fbcbc599baf1c24252dfc73efefc
- https://git.kernel.org/stable/c/8321b17789f614414206af07e17ce4751c95dc76
- https://git.kernel.org/stable/c/8da2b7bdb47e94bbc4062a3978c708926bcb022c
- https://git.kernel.org/stable/c/906c81dba8ee8057523859b5e1a2479e9fd34860
- https://git.kernel.org/stable/c/9e649471b396fa0139d53919354ce1eace9b9a24
- https://git.kernel.org/stable/c/af98940dd33c9f9e1beb4f71c0a39260100e2a65
- https://git.kernel.org/stable/c/da42761181627e9bdc37d18368b827948a583929
- https://git.kernel.org/stable/c/f76729662650cd7bc8f8194e057af381370349a7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49492.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49492
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
