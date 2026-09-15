# [H] batman-adv: reject new tp_meter sessions during teardown

## Summary
Severity: High
Advisory: CVE-2026-46206
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46206
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.90, >=6.13.0 <6.18.32, >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: reject new tp_meter sessions during teardown

Prevent tp_meter from starting new sender or receiver sessions after
mesh_state has left BATADV_MESH_ACTIVE.

## References
- https://git.kernel.org/stable/c/0a7a840074c9ca5ebffc9c52358c8ea55828ec71
- https://git.kernel.org/stable/c/3243543592425beec83d453793e9d27caa0d8e66
- https://git.kernel.org/stable/c/52e6ec3e972cf27792cc1559874dbee19f286869
- https://git.kernel.org/stable/c/ca39545cf07c142b39d474a1439a046bf28def3d
- https://git.kernel.org/stable/c/dcff44644bb518598b1a6be722706d6174b2f6a1
- https://git.kernel.org/stable/c/e1e2194cc725ec1d41f9412496212f0fa0519c36
- https://git.kernel.org/stable/c/e4a3c4a4c8f6efd243c3e448c05b7bebcbf7b3b6
- https://git.kernel.org/stable/c/ff93f86ecbb50a4709c403fc279a396e308edde5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46206.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46206
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
