# [H] Bluetooth: fix locking in hci_conn_request_evt() with HCI_PROTO_DEFER

## Summary
Severity: High
Advisory: CVE-2026-53072
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53072
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: fix locking in hci_conn_request_evt() with HCI_PROTO_DEFER

When protocol sets HCI_PROTO_DEFER, hci_conn_request_evt() calls
hci_connect_cfm(conn) without hdev->lock. Generally hci_connect_cfm()
assumes it is held, and if conn is deleted concurrently -> UAF.

Only SCO and ISO set HCI_PROTO_DEFER and only for defer setup listen,
and HCI_EV_CONN_REQUEST is not generated for ISO.  In the non-deferred
listening socket code paths, hci_connect_cfm(conn) is called with
hdev->lock held.

Fix by holding the lock.

## References
- https://git.kernel.org/stable/c/385b2d0468a0871fc716c549fa3b0c257c7dbcb3
- https://git.kernel.org/stable/c/541d5bf9b5afaf41090b2a3aa7b47f2db2ff801f
- https://git.kernel.org/stable/c/5c7209a341ff2ac338b2b0375c34a307b37c9ac2
- https://git.kernel.org/stable/c/60e3f4ff02d1f2d55bfbf2ca32a97285a9771ee4
- https://git.kernel.org/stable/c/6b4d226d01ab7da0d2027a2a1e3a6079152e5065
- https://git.kernel.org/stable/c/9d4a6c0f43fc5e4d4f062e8e450e5483eb74176e
- https://git.kernel.org/stable/c/c27224daf0b08efbb2b24ed64b6139b294f5473a
- https://git.kernel.org/stable/c/c7777f534a8018ae4bb1c80d8925af4df588a314
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53072.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53072
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
