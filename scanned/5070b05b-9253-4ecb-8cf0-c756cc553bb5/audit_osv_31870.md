# [H] slimbus: messaging: Free transaction ID in delayed interrupt scenario

## Summary
Severity: High
Advisory: CVE-2025-21914
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21914
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.131, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

slimbus: messaging: Free transaction ID in delayed interrupt scenario

In case of interrupt delay for any reason, slim_do_transfer()
returns timeout error but the transaction ID (TID) is not freed.
This results into invalid memory access inside
qcom_slim_ngd_rx_msgq_cb() due to invalid TID.

Fix the issue by freeing the TID in slim_do_transfer() before
returning timeout error to avoid invalid memory access.

Call trace:
__memcpy_fromio+0x20/0x190
qcom_slim_ngd_rx_msgq_cb+0x130/0x290 [slim_qcom_ngd_ctrl]
vchan_complete+0x2a0/0x4a0
tasklet_action_common+0x274/0x700
tasklet_action+0x28/0x3c
_stext+0x188/0x620
run_ksoftirqd+0x34/0x74
smpboot_thread_fn+0x1d8/0x464
kthread+0x178/0x238
ret_from_fork+0x10/0x20
Code: aa0003e8 91000429 f100044a 3940002b (3800150b)
---[ end trace 0fe00bec2b975c99 ]---
Kernel panic - not syncing: Oops: Fatal exception in interrupt.

## References
- https://git.kernel.org/stable/c/09d34c4cbc38485c7514069f25348e439555b282
- https://git.kernel.org/stable/c/0c541c8f6da23e0b92f0a6216d899659a7572074
- https://git.kernel.org/stable/c/18ae4cee05c310c299ba75d7477dcf34be67aa16
- https://git.kernel.org/stable/c/6abf3d8bb51cbaf886c3f08109a0462890b10db6
- https://git.kernel.org/stable/c/a32e5198a9134772eb03f7b72a7849094c55bda9
- https://git.kernel.org/stable/c/cec8c0ac173fe5321f03fdb1a09a9cb69bc9a9fe
- https://git.kernel.org/stable/c/dcb0d43ba8eb9517e70b1a0e4b0ae0ab657a0e5a
- https://git.kernel.org/stable/c/faac8e894014e8167471a8e4a5eb35a8fefbb82a
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21914.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21914
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
