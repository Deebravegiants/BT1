# [H] media: dvb-core: fix wrong reinitialization of ringbuffer on reopen

## Summary
Severity: High
Advisory: CVE-2026-23253
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-23253
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.17 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.77, >=6.13.0 <6.18.17, >=6.19.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: dvb-core: fix wrong reinitialization of ringbuffer on reopen

dvb_dvr_open() calls dvb_ringbuffer_init() when a new reader opens the
DVR device.  dvb_ringbuffer_init() calls init_waitqueue_head(), which
reinitializes the waitqueue list head to empty.

Since dmxdev->dvr_buffer.queue is a shared waitqueue (all opens of the
same DVR device share it), this orphans any existing waitqueue entries
from io_uring poll or epoll, leaving them with stale prev/next pointers
while the list head is reset to {self, self}.

The waitqueue and spinlock in dvr_buffer are already properly
initialized once in dvb_dmxdev_init().  The open path only needs to
reset the buffer data pointer, size, and read/write positions.

Replace the dvb_ringbuffer_init() call in dvb_dvr_open() with direct
assignment of data/size and a call to dvb_ringbuffer_reset(), which
properly resets pread, pwrite, and error with correct memory ordering
without touching the waitqueue or spinlock.

## References
- https://git.kernel.org/stable/c/32eb8e4adc207ef31bc6e5ae56bab940b0176066
- https://git.kernel.org/stable/c/527cfa8a3486b3555c5c15e2f62be484a11398dc
- https://git.kernel.org/stable/c/af050ab44fa1b1897a940d7d756e512232f5e5df
- https://git.kernel.org/stable/c/bfbc0b5b32a8f28ce284add619bf226716a59bc0
- https://git.kernel.org/stable/c/cfd94642025e6f71c8f754bdec0800ee95e4f3dd
- https://git.kernel.org/stable/c/d71781bad59b1c9d60d7068004581f9bf19c0c9d
- https://git.kernel.org/stable/c/f1e520ca2e83ece6731af6167c9e5e16931ecba0
- https://git.kernel.org/stable/c/fb378cf89be434ed1f10ab79cc4788fba8ae868d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23253.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23253
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
