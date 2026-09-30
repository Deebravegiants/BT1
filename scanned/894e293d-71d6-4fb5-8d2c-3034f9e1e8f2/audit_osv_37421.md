# [H] wifi: wlcore: Return -ENOMEM instead of -EAGAIN if there is not enough headroom

## Summary
Severity: High
Advisory: CVE-2026-31552
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31552
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: wlcore: Return -ENOMEM instead of -EAGAIN if there is not enough headroom

Since upstream commit e75665dd0968 ("wifi: wlcore: ensure skb headroom
before skb_push"), wl1271_tx_allocate() and with it
wl1271_prepare_tx_frame() returns -EAGAIN if pskb_expand_head() fails.
However, in wlcore_tx_work_locked(), a return value of -EAGAIN from
wl1271_prepare_tx_frame() is interpreted as the aggregation buffer being
full. This causes the code to flush the buffer, put the skb back at the
head of the queue, and immediately retry the same skb in a tight while
loop.

Because wlcore_tx_work_locked() holds wl->mutex, and the retry happens
immediately with GFP_ATOMIC, this will result in an infinite loop and a
CPU soft lockup. Return -ENOMEM instead so the packet is dropped and
the loop terminates.

The problem was found by an experimental code review agent based on
gemini-3.1-pro while reviewing backports into v6.18.y.

## References
- https://git.kernel.org/stable/c/12f9eef39e49716c763714bfda835a733d5f6dea
- https://git.kernel.org/stable/c/46c670ff1ff466e5eccb3940f726586473dc053c
- https://git.kernel.org/stable/c/980f793645540ca7a6318165cc12f49d5febeb99
- https://git.kernel.org/stable/c/a6dc74209462c4fe5a88718d2f3a5286886081c8
- https://git.kernel.org/stable/c/ceb46b40b021d21911ff8608ce4ed33c1264ad2f
- https://git.kernel.org/stable/c/cfa64e2b3717be1da7c4c1aff7268a009e8c1610
- https://git.kernel.org/stable/c/deb353d9bb009638b7762cae2d0b6e8fdbb41a69
- https://git.kernel.org/stable/c/f2c06d718a7b85cbc59ceaa2ff3f46b178ac709c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31552.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31552
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
