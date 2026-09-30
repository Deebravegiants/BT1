# [H] wifi: mac80211: don't flush non-uploaded STAs

## Summary
Severity: High
Advisory: CVE-2025-21828
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2025-21828
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: don't flush non-uploaded STAs

If STA state is pre-moved to AUTHORIZED (such as in IBSS
scenarios) and insertion fails, the station is freed.
In this case, the driver never knew about the station,
so trying to flush it is unexpected and may crash.

Check if the sta was uploaded to the driver before and
fix this.

## References
- https://git.kernel.org/stable/c/9efb5531271fa7ebae993b2a33a705d9947c7ce6
- https://git.kernel.org/stable/c/aa3ce3f8fafa0b8fb062f28024855ea8cb3f3450
- https://git.kernel.org/stable/c/cd10b7fcb95a6a86c67adc54304c59a578ab16af
- https://git.kernel.org/stable/c/cf21ef3d430847ba864bbc9b2774fffcc03ce321
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21828.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21828
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
