# [H] Bluetooth: MGMT: fix crash in set_mesh_sync and set_mesh_complete

## Summary
Severity: High
Advisory: CVE-2025-40213
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-24
Source: https://osv.dev/vulnerability/CVE-2025-40213
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: MGMT: fix crash in set_mesh_sync and set_mesh_complete

There is a BUG: KASAN: stack-out-of-bounds in set_mesh_sync due to
memcpy from badly declared on-stack flexible array.

Another crash is in set_mesh_complete() due to double list_del via
mgmt_pending_valid + mgmt_pending_remove.

Use DEFINE_FLEX to declare the flexible array right, and don't memcpy
outside bounds.

As mgmt_pending_valid removes the cmd from list, use mgmt_pending_free,
and also report status on error.

## References
- https://git.kernel.org/stable/c/1c9aca1787e8395a2c59fef20e914467958969c5
- https://git.kernel.org/stable/c/5c19daa93d9af29f1f46251b47e1ea66bcc8d679
- https://git.kernel.org/stable/c/e8785404de06a69d89dcdd1e9a0b6ea42dc6d327
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40213.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40213
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
