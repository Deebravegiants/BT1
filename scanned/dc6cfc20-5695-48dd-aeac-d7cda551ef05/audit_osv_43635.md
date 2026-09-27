# [H] Bluetooth: mgmt: fix UAF in pair command cancellation

## Summary
Severity: High
Advisory: CVE-2026-74510
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74510
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <6.1.184, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: mgmt: fix UAF in pair command cancellation

The pairing completion and authentication failure callbacks look up the
pending MGMT_OP_PAIR_DEVICE command by walking hdev->mgmt_pending. The
lookup returned a command that was still linked on the shared pending list,
without keeping mgmt_pending_lock held for the later dereference and
removal.

A concurrent MGMT_OP_CANCEL_PAIR_DEVICE request can remove and free the
same pending command before the callback uses it. The reverse race is also
possible when cancel_pair_device() gets a command from pending_find() and a
callback removes it before the cancel path dereferences it. This can lead
to a use-after-free and a second list_del().

Make the pairing lookup helpers transfer ownership of the pending command
by removing it from hdev->mgmt_pending while holding mgmt_pending_lock.
The callbacks and cancel path then complete the command and free it
directly, so racing paths cannot find or free the same command again. Take
a temporary hci_conn reference in cancel_pair_device() because the command
completion drops the reference stored in the pending command.

## References
- https://git.kernel.org/stable/c/50af4280a587c9971b5388cbc438f1324e626b7b
- https://git.kernel.org/stable/c/51be7280980fddc90ebe874a69c2fe8ab02bb46a
- https://git.kernel.org/stable/c/7c2a152a897cd1c184b2051484d4f74d803e7f4a
- https://git.kernel.org/stable/c/86ed4dd6548ccf277bc691bc912ca06e76b9d80c
- https://git.kernel.org/stable/c/c569def320aa8b1fde89227e2ea96606790fd86d
- https://git.kernel.org/stable/c/d0a7b48ad0921bd88effaee10bf970ab1d5d0ddd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74510.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74510
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
