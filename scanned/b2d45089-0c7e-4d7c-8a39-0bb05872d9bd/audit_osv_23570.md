# [M] Bluetooth: fix null ptr deref on hci_sync_conn_complete_evt

## Summary
Severity: Medium
Advisory: CVE-2022-49139
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49139
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <5.4.231, >=5.5.0 <5.10.167, >=5.11.0 <5.15.92, >=5.16.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: fix null ptr deref on hci_sync_conn_complete_evt

This event is just specified for SCO and eSCO link types.
On the reception of a HCI_Synchronous_Connection_Complete for a BDADDR
of an existing LE connection, LE link type and a status that triggers the
second case of the packet processing a NULL pointer dereference happens,
as conn->link is NULL.

## References
- https://git.kernel.org/stable/c/0f9db1209f59844839175b5b907d3778cafde93d
- https://git.kernel.org/stable/c/1c1291a84e94f6501644634c97544bb8291e9a1a
- https://git.kernel.org/stable/c/3afee2118132e93e5f6fa636dfde86201a860ab3
- https://git.kernel.org/stable/c/c1aa0dd52db4ce888be0bd820c3fa918d350ca0b
- https://git.kernel.org/stable/c/f61c23e73dc653b957781066abfa8105c3fa3f5b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49139.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49139
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
