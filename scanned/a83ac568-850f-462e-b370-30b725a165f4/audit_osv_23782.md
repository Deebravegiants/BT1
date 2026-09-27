# [H] mt76: fix tx status related use-after-free race on station removal

## Summary
Severity: High
Advisory: CVE-2022-49479
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49479
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mt76: fix tx status related use-after-free race on station removal

There is a small race window where ongoing tx activity can lead to a skb
getting added to the status tracking idr after that idr has already been
cleaned up, which will keep the wcid linked in the status poll list.
Fix this by only adding status skbs if the wcid pointer is still assigned
in dev->wcid, which gets cleared early by mt76_sta_pre_rcu_remove

## References
- https://git.kernel.org/stable/c/ddd426d72aca4054045a9bd3b80a4ce1d398f11f
- https://git.kernel.org/stable/c/ef7f9f894cfd0b2e471206409a529af4a26ddd55
- https://git.kernel.org/stable/c/fcfe1b5e162bf473c1d47760962cec8523c00466
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49479.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49479
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
