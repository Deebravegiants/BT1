# [H] wifi: mac80211: do not pass a stopped vif to the driver in .get_txpower

## Summary
Severity: High
Advisory: CVE-2024-50237
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50237
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.171, >=5.16.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: do not pass a stopped vif to the driver in .get_txpower

Avoid potentially crashing in the driver because of uninitialized private data

## References
- https://git.kernel.org/stable/c/393b6bc174b0dd21bb2a36c13b36e62fc3474a23
- https://git.kernel.org/stable/c/3ccf525a73d48e814634847f6d4a6150c6f0dffc
- https://git.kernel.org/stable/c/78b698fbf37208ee921ee4cedea75b5d33d6ea9f
- https://git.kernel.org/stable/c/8f6cd4d5bb7406656835a90e4f1a2192607f0c21
- https://git.kernel.org/stable/c/b0b862aa3dbcd16b3c4715259a825f48ca540088
- https://git.kernel.org/stable/c/b2bcbe5450b20641f512d6b26c6b256a5a4f847f
- https://git.kernel.org/stable/c/c21efba8b5a86537ccdf43f77536bad02f82776c
- https://git.kernel.org/stable/c/ee35c423042c9e04079fdee3db545135d609d6ea
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50237.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50237
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
