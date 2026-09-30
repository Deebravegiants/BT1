# [C] RDMA/rtrs-clt: Reset cid to con_num - 1 to stay in bounds

## Summary
Severity: Critical
Advisory: CVE-2024-47695
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47695
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rtrs-clt: Reset cid to con_num - 1 to stay in bounds

In the function init_conns(), after the create_con() and create_cm() for
loop if something fails. In the cleanup for loop after the destroy tag, we
access out of bound memory because cid is set to clt_path->s.con_num.

This commits resets the cid to clt_path->s.con_num - 1, to stay in bounds
in the cleanup loop later.

## References
- https://git.kernel.org/stable/c/01b9be936ee8839ab9f83a7e84ee02ac6c8303c4
- https://git.kernel.org/stable/c/0429a4e972082e3a2351da414b1c017daaf8aed2
- https://git.kernel.org/stable/c/1c50e0265fa332c94a4a182e4efa0fc70d8fad94
- https://git.kernel.org/stable/c/3e4289b29e216a55d08a89e126bc0b37cbad9f38
- https://git.kernel.org/stable/c/5ac73f8191f3de41fef4f934d84d97f3aadb301f
- https://git.kernel.org/stable/c/c8b7f3d9fada0d4b4b7db86bf7345cd61f1d972e
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47695.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47695
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
