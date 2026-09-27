# [H] Bluetooth: Avoid potential use-after-free in hci_error_reset

## Summary
Severity: High
Advisory: CVE-2024-26801
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/CVE-2024-26801
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <4.19.309, >=4.20.0 <5.4.271, >=5.5.0 <5.10.212, >=5.11.0 <5.15.151, >=5.16.0 <6.1.81, >=6.2.0 <6.6.21, >=6.7.0 <6.7.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: Avoid potential use-after-free in hci_error_reset

While handling the HCI_EV_HARDWARE_ERROR event, if the underlying
BT controller is not responding, the GPIO reset mechanism would
free the hci_dev and lead to a use-after-free in hci_error_reset.

Here's the call trace observed on a ChromeOS device with Intel AX201:
   queue_work_on+0x3e/0x6c
   __hci_cmd_sync_sk+0x2ee/0x4c0 [bluetooth <HASH:3b4a6>]
   ? init_wait_entry+0x31/0x31
   __hci_cmd_sync+0x16/0x20 [bluetooth <HASH:3b4a 6>]
   hci_error_reset+0x4f/0xa4 [bluetooth <HASH:3b4a 6>]
   process_one_work+0x1d8/0x33f
   worker_thread+0x21b/0x373
   kthread+0x13a/0x152
   ? pr_cont_work+0x54/0x54
   ? kthread_blkcg+0x31/0x31
    ret_from_fork+0x1f/0x30

This patch holds the reference count on the hci_dev while processing
a HCI_EV_HARDWARE_ERROR event to avoid potential crash.

## References
- https://git.kernel.org/stable/c/2449007d3f73b2842c9734f45f0aadb522daf592
- https://git.kernel.org/stable/c/2ab9a19d896f5a0dd386e1f001c5309bc35f433b
- https://git.kernel.org/stable/c/45085686b9559bfbe3a4f41d3d695a520668f5e1
- https://git.kernel.org/stable/c/6dd0a9dfa99f8990a08eb8fdd8e79bee31c7d8e2
- https://git.kernel.org/stable/c/98fb98fd37e42fd4ce13ff657ea64503e24b6090
- https://git.kernel.org/stable/c/da4569d450b193e39e87119fd316c0291b585d14
- https://git.kernel.org/stable/c/dd594cdc24f2e48dab441732e6dfcafd6b0711d1
- https://git.kernel.org/stable/c/e0b278650f07acf2e0932149183458468a731c03
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26801.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26801
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
