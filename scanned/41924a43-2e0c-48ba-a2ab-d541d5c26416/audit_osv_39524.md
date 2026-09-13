# [H] Bluetooth: hci_event: fix potential UAF in SSP passkey handlers

## Summary
Severity: High
Advisory: CVE-2026-46056
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46056
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_event: fix potential UAF in SSP passkey handlers

hci_conn lookup and field access must be covered by hdev lock in
hci_user_passkey_notify_evt() and hci_keypress_notify_evt(), otherwise
the connection can be freed concurrently.

Extend the hci_dev_lock critical section to cover all conn usage in both
handlers.

Keep the existing keypress notification behavior unchanged by routing
the early exits through a common unlock path.

## References
- https://git.kernel.org/stable/c/01a6431766c35dfedb86e0cb5d3fc80c6d604a47
- https://git.kernel.org/stable/c/204028af77a265e31ceb4ba7f643349a3cca72b2
- https://git.kernel.org/stable/c/85fa3512048793076eef658f66489112dcc91993
- https://git.kernel.org/stable/c/8c6443bb9257b780986fb67ec08565bf48ecb8d7
- https://git.kernel.org/stable/c/b6ae482f88654db407c8c17619d4b62959b903ef
- https://git.kernel.org/stable/c/d28311539ac9f65e29308ea219ecaa48aa5e76e5
- https://git.kernel.org/stable/c/e08d75753db17aa943d7622f09d9c217b5bfd3b8
- https://git.kernel.org/stable/c/ea18732d2614557e59f4c0d8cdbe6611aeab33b7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46056.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46056
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
