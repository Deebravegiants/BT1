# [H] can: dev: fix skb drop check

## Summary
Severity: High
Advisory: CVE-2022-49844
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49844
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: dev: fix skb drop check

In commit a6d190f8c767 ("can: skb: drop tx skb if in listen only
mode") the priv->ctrlmode element is read even on virtual CAN
interfaces that do not create the struct can_priv at startup. This
out-of-bounds read may lead to CAN frame drops for virtual CAN
interfaces like vcan and vxcan.

This patch mainly reverts the original commit and adds a new helper
for CAN interface drivers that provide the required information in
struct can_priv.

[mkl: patch pch_can, too]

## References
- https://git.kernel.org/stable/c/386c49fe31ee748e053860b3bac7794a933ac9ac
- https://git.kernel.org/stable/c/ae64438be1923e3c1102d90fd41db7afcfaf54cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49844.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49844
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
