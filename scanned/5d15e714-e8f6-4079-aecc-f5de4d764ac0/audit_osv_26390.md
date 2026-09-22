# [M] Bluetooth: Fix possible deadlock in rfcomm_sk_state_change

## Summary
Severity: Medium
Advisory: CVE-2023-53016
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-53016
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.91, >=5.16.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: Fix possible deadlock in rfcomm_sk_state_change

syzbot reports a possible deadlock in rfcomm_sk_state_change [1].
While rfcomm_sock_connect acquires the sk lock and waits for
the rfcomm lock, rfcomm_sock_release could have the rfcomm
lock and hit a deadlock for acquiring the sk lock.
Here's a simplified flow:

rfcomm_sock_connect:
  lock_sock(sk)
  rfcomm_dlc_open:
    rfcomm_lock()

rfcomm_sock_release:
  rfcomm_sock_shutdown:
    rfcomm_lock()
    __rfcomm_dlc_close:
        rfcomm_k_state_change:
	  lock_sock(sk)

This patch drops the sk lock before calling rfcomm_dlc_open to
avoid the possible deadlock and holds sk's reference count to
prevent use-after-free after rfcomm_dlc_open completes.

## References
- https://git.kernel.org/stable/c/17511bd84871f4a6106cb335616e086880313f3f
- https://git.kernel.org/stable/c/1d80d57ffcb55488f0ec0b77928d4f82d16b6a90
- https://git.kernel.org/stable/c/98aec50ff7f60cc6f2d6a4396b475c547e58b04d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53016.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53016
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
