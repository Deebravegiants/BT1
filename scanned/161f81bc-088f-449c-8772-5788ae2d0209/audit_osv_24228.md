# [H] wifi: mt76: mt76x0: fix oob access in mt76x0_phy_get_target_power

## Summary
Severity: High
Advisory: CVE-2022-50508
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2022-50508
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: mt76x0: fix oob access in mt76x0_phy_get_target_power

After 'commit ba45841ca5eb ("wifi: mt76: mt76x02: simplify struct
mt76x02_rate_power")', mt76x02 relies on ht[0-7] rate_power data for
vht mcs{0,7}, while it uses vth[0-1] rate_power for vht mcs {8,9}.
Fix a possible out-of-bound access in mt76x0_phy_get_target_power routine.

## References
- https://git.kernel.org/stable/c/6e1abc51c945663bddebfa1beb9590ff5b250eb7
- https://git.kernel.org/stable/c/bf425c5d7ef6fb4083c1e0d46440f886127b5ee5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50508.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50508
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
