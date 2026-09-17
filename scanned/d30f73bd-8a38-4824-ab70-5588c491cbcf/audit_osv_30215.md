# [M] irqchip/gic-v4: Don't allow a VMOVP on a dying VPE

## Summary
Severity: Medium
Advisory: CVE-2024-50192
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50192
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.228, >=5.11.0 <5.15.169, >=5.16.0 <6.1.114, >=6.2.0 <6.6.58, >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

irqchip/gic-v4: Don't allow a VMOVP on a dying VPE

Kunkun Jiang reported that there is a small window of opportunity for
userspace to force a change of affinity for a VPE while the VPE has already
been unmapped, but the corresponding doorbell interrupt still visible in
/proc/irq/.

Plug the race by checking the value of vmapp_count, which tracks whether
the VPE is mapped ot not, and returning an error in this case.

This involves making vmapp_count common to both GICv4.1 and its v4.0
ancestor.

## References
- https://git.kernel.org/stable/c/01282ab5182f85e42234df2ff42f0ce790f465ff
- https://git.kernel.org/stable/c/1442ee0011983f0c5c4b92380e6853afb513841a
- https://git.kernel.org/stable/c/64b12b061c5488e2d69e67c4eaae5da64fd30bfe
- https://git.kernel.org/stable/c/755b9532c885b8761fb135fedcd705e21e61cccb
- https://git.kernel.org/stable/c/b7d7b7fc876f836f40bf48a87e07ea18756ba196
- https://git.kernel.org/stable/c/d960505a869e66184fff97fb334980a5b797c7c6
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50192.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50192
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
