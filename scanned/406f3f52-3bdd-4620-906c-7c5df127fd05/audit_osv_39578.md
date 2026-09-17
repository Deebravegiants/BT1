# [H] batman-adv: fix integer overflow on buff_pos

## Summary
Severity: High
Advisory: CVE-2026-46198
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46198
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.90, >=6.13.0 <6.18.32, >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: fix integer overflow on buff_pos

Fixing an integer overflow present in batadv_iv_ogm_send_to_if. The size
check is done using the int type in batadv_iv_ogm_aggr_packet whereas the
buff_pos variable uses the s16 type. This could lead to an out-of-bound
read.

## References
- https://git.kernel.org/stable/c/0799e5943611006b346b8813c7daf7dd5aa26bfd
- https://git.kernel.org/stable/c/10bb1f366d884d506c38a947b43026a75d1afe9a
- https://git.kernel.org/stable/c/867cd090760e8f5cd206f387b47ff9c56fac04e9
- https://git.kernel.org/stable/c/96c9c0ed9a9579a9085765aceaa4556a6666eb82
- https://git.kernel.org/stable/c/974542d1efc48b7e9fe16184e647615cba39969b
- https://git.kernel.org/stable/c/b252797bfced986d6d92ec2f4cfcca842ce8aa78
- https://git.kernel.org/stable/c/bf872db54f91ffe70104b98c20068b2d5910e018
- https://git.kernel.org/stable/c/f61499359fa529f0d45a53bf7c573a49eb6322e6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46198.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46198
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
