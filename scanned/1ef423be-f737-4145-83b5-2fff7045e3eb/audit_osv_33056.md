# [H] wifi: rtw89: mcc: prevent shift wrapping in rtw89_core_mlsr_switch()

## Summary
Severity: High
Advisory: CVE-2025-38657
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-38657
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtw89: mcc: prevent shift wrapping in rtw89_core_mlsr_switch()

The "link_id" value comes from the user via debugfs.  If it's larger
than BITS_PER_LONG then that would result in shift wrapping and
potentially an out of bounds access later.  In fact, we can limit it
to IEEE80211_MLD_MAX_NUM_LINKS (15).

Fortunately, only root can write to debugfs files so the security
impact is minimal.

## References
- https://git.kernel.org/stable/c/417cfa9cc44fbe6bceab786f9a4ee5a210f1288e
- https://git.kernel.org/stable/c/53cf488927a0f79968f9c03c4d1e00d2a79731c3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38657.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38657
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
