# [H] wifi: ath11k: rely on mac80211 debugfs handling for vif

## Summary
Severity: High
Advisory: CVE-2024-26637
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2024-26637
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath11k: rely on mac80211 debugfs handling for vif

mac80211 started to delete debugfs entries in certain cases, causing a
ath11k to crash when it tried to delete the entries later. Fix this by
relying on mac80211 to delete the entries when appropriate and adding
them from the vif_add_debugfs handler.

## References
- https://git.kernel.org/stable/c/556857aa1d0855aba02b1c63bc52b91ec63fc2cc
- https://git.kernel.org/stable/c/aa74ce30a8a40d19a4256de4ae5322e71344a274
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26637.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26637
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
