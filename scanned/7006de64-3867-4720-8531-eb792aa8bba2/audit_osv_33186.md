# [H] wifi: mt76: mt7915: fix list corruption after hardware restart

## Summary
Severity: High
Advisory: CVE-2025-39862
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-39862
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: mt7915: fix list corruption after hardware restart

Since stations are recreated from scratch, all lists that wcids are added
to must be cleared before calling ieee80211_restart_hw.
Set wcid->sta = 0 for each wcid entry in order to ensure that they are
not added again before they are ready.

## References
- https://git.kernel.org/stable/c/065c79df595af21d6d1b27d642860faa1d938774
- https://git.kernel.org/stable/c/8fa8eb52bc2eb08d93202863b5fc478e0bebc00c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39862.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39862
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
