# [H] wifi: mac80211: fix invalid drv_sta_pre_rcu_remove calls for non-uploaded sta

## Summary
Severity: High
Advisory: CVE-2023-53229
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53229
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <4.14.313, >=4.15.0 <4.19.281, >=4.20.0 <5.4.241, >=5.5.0 <5.10.178, >=5.11.0 <5.15.107, >=5.16.0 <6.1.24, >=6.2.0 <6.2.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: fix invalid drv_sta_pre_rcu_remove calls for non-uploaded sta

Avoid potential data corruption issues caused by uninitialized driver
private data structures.

## References
- https://git.kernel.org/stable/c/022c8320d9eb7394538bd716fa1a07a5ed92621b
- https://git.kernel.org/stable/c/12b220a6171faf10638ab683a975cadcf1a352d6
- https://git.kernel.org/stable/c/30c5a016a37a668c1c07442cf94de6e99ea7417a
- https://git.kernel.org/stable/c/3fe20515449a80a177526d2ecd13b43f6ee41aeb
- https://git.kernel.org/stable/c/73752a39e2a6e38eee3ba90ece2ded598ea88006
- https://git.kernel.org/stable/c/7e68d7c640d41d8a371b8f6c2d2682ea437cbe21
- https://git.kernel.org/stable/c/a3593082e0dadf87f17ea4ca9fa0210caaa2aebf
- https://git.kernel.org/stable/c/db8d32d6b25fdb75c387daee496b96209d477780
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53229.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53229
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
