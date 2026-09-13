# [M] octeontx2-pf: handle otx2_mbox_get_rsp errors in otx2_ethtool.c

## Summary
Severity: Medium
Advisory: CVE-2024-56728
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56728
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-pf: handle otx2_mbox_get_rsp errors in otx2_ethtool.c

Add error pointer check after calling otx2_mbox_get_rsp().

## References
- https://git.kernel.org/stable/c/05a6ce174c0c724e5914e1e5efd826bab8f382b4
- https://git.kernel.org/stable/c/2db2194727b1f49a5096c1c3981adef1b7638733
- https://git.kernel.org/stable/c/55c41b97001a09bb490ffa2e667e251d75d15ab1
- https://git.kernel.org/stable/c/5ff9de1f2712cbca53da2e37d831eea7ffcb43b6
- https://git.kernel.org/stable/c/6cda142cee032b8fe65ee11f78721721c3988feb
- https://git.kernel.org/stable/c/c0f64fd73b60aee85f88c270c9d714ead27a7b7a
- https://git.kernel.org/stable/c/e26f8eac6bb20b20fdb8f7dc695711ebce4c7c5c
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56728.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56728
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
