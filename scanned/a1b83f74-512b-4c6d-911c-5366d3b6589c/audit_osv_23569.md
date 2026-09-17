# [H] Bluetooth: hci_event: Ignore multiple conn complete events

## Summary
Severity: High
Advisory: CVE-2022-49138
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49138
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.27 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_event: Ignore multiple conn complete events

When one of the three connection complete events is received multiple
times for the same handle, the device is registered multiple times which
leads to memory corruptions. Therefore, consequent events for a single
connection are ignored.

The conn->state can hold different values, therefore HCI_CONN_HANDLE_UNSET
is introduced to identify new connections. To make sure the events do not
contain this or another invalid handle HCI_CONN_HANDLE_MAX and checks
are introduced.

Buglink: https://bugzilla.kernel.org/show_bug.cgi?id=215497

## References
- https://git.kernel.org/stable/c/aa1ca580e3ffe62a2c5ea1c095b609b2943c5269
- https://git.kernel.org/stable/c/d5ebaa7c5f6f688959e8d40840b2249ede63b8ed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49138.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49138
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
