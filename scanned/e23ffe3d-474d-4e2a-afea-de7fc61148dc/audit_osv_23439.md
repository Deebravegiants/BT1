# [C] nvme-rdma: fix possible use-after-free in transport error_recovery work

## Summary
Severity: Critical
Advisory: CVE-2022-48788
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48788
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <4.19.231, >=4.20.0 <5.4.181, >=5.5.0 <5.10.102, >=5.11.0 <5.15.25, >=5.16.0 <5.16.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-rdma: fix possible use-after-free in transport error_recovery work

While nvme_rdma_submit_async_event_work is checking the ctrl and queue
state before preparing the AER command and scheduling io_work, in order
to fully prevent a race where this check is not reliable the error
recovery work must flush async_event_work before continuing to destroy
the admin queue after setting the ctrl state to RESETTING such that
there is no race .submit_async_event and the error recovery handler
itself changing the ctrl state.

## References
- https://git.kernel.org/stable/c/324f5bdc52ecb6a6dadb31a62823ef8c709d1439
- https://git.kernel.org/stable/c/5593f72d1922403c11749532e3a0aa4cf61414e9
- https://git.kernel.org/stable/c/646952b2210f19e584d2bf9eb5d092abdca2fcc1
- https://git.kernel.org/stable/c/b6bb1722f34bbdbabed27acdceaf585d300c5fd2
- https://git.kernel.org/stable/c/d411b2a5da68b8a130c23097014434ac140a2ace
- https://git.kernel.org/stable/c/ea86027ac467a055849c4945906f799e7f65ab99
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48788.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48788
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
