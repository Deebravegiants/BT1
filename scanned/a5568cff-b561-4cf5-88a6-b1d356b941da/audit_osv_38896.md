# [H] Bluetooth: hci_event: fix potential UAF in hci_le_remote_conn_param_req_evt

## Summary
Severity: High
Advisory: CVE-2026-43018
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43018
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_event: fix potential UAF in hci_le_remote_conn_param_req_evt

hci_conn lookup and field access must be covered by hdev lock in
hci_le_remote_conn_param_req_evt, otherwise it's possible it is freed
concurrently.

Extend the hci_dev_lock critical section to cover all conn usage.

## References
- https://git.kernel.org/stable/c/1d0bdbfe3e91c11f0a704c52443a9446a10d699c
- https://git.kernel.org/stable/c/59eecf0ffde15670e6a5e10c47be67f73d843b20
- https://git.kernel.org/stable/c/5fb69e1eeea9d6cba80517e9f058b56b34bc3a81
- https://git.kernel.org/stable/c/7cadb03be37e761130edb153544fe0770a842b19
- https://git.kernel.org/stable/c/b255531b27da336571411248c2a72a350662bd09
- https://git.kernel.org/stable/c/ea3cd36d7382d5f8309df04c275d20df139ed42c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43018.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43018
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
