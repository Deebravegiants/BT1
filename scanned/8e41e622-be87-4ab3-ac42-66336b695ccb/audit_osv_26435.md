# [M] wifi: mac80211_hwsim: Fix possible NULL dereference

## Summary
Severity: Medium
Advisory: CVE-2023-53209
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53209
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.42, >=6.2.0 <6.4.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211_hwsim: Fix possible NULL dereference

In a call to mac80211_hwsim_select_tx_link() the sta pointer might
be NULL, thus need to check that it is not NULL before accessing it.

## References
- https://git.kernel.org/stable/c/0cc80943ef518a1c51a1111e9346d1daf11dd545
- https://git.kernel.org/stable/c/a8a20fed3e05b3a6866c5c58855deaf3c217ccd6
- https://git.kernel.org/stable/c/d0124848c7940aba73492e282506b32a13f2e30e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53209.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53209
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
