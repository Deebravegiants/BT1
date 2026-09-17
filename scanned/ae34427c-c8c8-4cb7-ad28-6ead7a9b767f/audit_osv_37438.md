# [H] ALSA: ctxfi: Limit PTP to a single page

## Summary
Severity: High
Advisory: CVE-2026-31602
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31602
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: ctxfi: Limit PTP to a single page

Commit 391e69143d0a increased CT_PTP_NUM from 1 to 4 to support 256
playback streams, but the additional pages are not used by the card
correctly. The CT20K2 hardware already has multiple VMEM_PTPAL
registers, but using them separately would require refactoring the
entire virtual memory allocation logic.

ct_vm_map() always uses PTEs in vm->ptp[0].area regardless of
CT_PTP_NUM. On AMD64 systems, a single PTP covers 512 PTEs (2M). When
aggregate memory allocations exceed this limit, ct_vm_map() tries to
access beyond the allocated space and causes a page fault:

  BUG: unable to handle page fault for address: ffffd4ae8a10a000
  Oops: Oops: 0002 [#1] SMP PTI
  RIP: 0010:ct_vm_map+0x17c/0x280 [snd_ctxfi]
  Call Trace:
  atc_pcm_playback_prepare+0x225/0x3b0
  ct_pcm_playback_prepare+0x38/0x60
  snd_pcm_do_prepare+0x2f/0x50
  snd_pcm_action_single+0x36/0x90
  snd_pcm_action_nonatomic+0xbf/0xd0
  snd_pcm_ioctl+0x28/0x40
  __x64_sys_ioctl+0x97/0xe0
  do_syscall_64+0x81/0x610
  entry_SYSCALL_64_after_hwframe+0x76/0x7e

Revert CT_PTP_NUM to 1. The 256 SRC_RESOURCE_NUM and playback_count
remain unchanged.

## References
- https://git.kernel.org/stable/c/2b4331c08c0b385598b4d8ccd71e93ab3f4b2578
- https://git.kernel.org/stable/c/365c36e1a126c6aa1aecedd3a351bcabc66f0c29
- https://git.kernel.org/stable/c/3fd0685d7fef68c2d8a04876bcf9eaa0724ad6a5
- https://git.kernel.org/stable/c/452894005b4abe141b11fe01e7bfe152e6d3860f
- https://git.kernel.org/stable/c/ad9011a795407093dcf507f6e5da1828987b4b47
- https://git.kernel.org/stable/c/b7f5ecd13cce8c2f8fa5a84c9aab65997142577e
- https://git.kernel.org/stable/c/c5908160e17cb56e1f61fbaee08adc21083f4933
- https://git.kernel.org/stable/c/de8016fb0904d68ac886e375069535996baa42ee
- https://git.kernel.org/stable/c/e9418da50d9e5c496c22fe392e4ad74c038a94eb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31602.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31602
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
