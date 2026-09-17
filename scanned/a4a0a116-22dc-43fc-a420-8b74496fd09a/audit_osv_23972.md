# [H] Bluetooth: Fix a buffer overflow in mgmt_mesh_add()

## Summary
Severity: High
Advisory: CVE-2022-49754
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2022-49754
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: Fix a buffer overflow in mgmt_mesh_add()

Smatch Warning:
net/bluetooth/mgmt_util.c:375 mgmt_mesh_add() error: __memcpy()
'mesh_tx->param' too small (48 vs 50)

Analysis:

'mesh_tx->param' is array of size 48. This is the destination.
u8 param[sizeof(struct mgmt_cp_mesh_send) + 29]; // 19 + 29 = 48.

But in the caller 'mesh_send' we reject only when len > 50.
len > (MGMT_MESH_SEND_SIZE + 31) // 19 + 31 = 50.

## References
- https://git.kernel.org/stable/c/2185e0fdbb2137f22a9dd9fcbf6481400d56299b
- https://git.kernel.org/stable/c/ed818fd8c531abf561b379995ee7cc4c68029464
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49754.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49754
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
