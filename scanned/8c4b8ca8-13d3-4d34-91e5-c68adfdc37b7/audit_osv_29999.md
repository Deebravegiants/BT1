# [M] wifi: rtw89: check return value of ieee80211_probereq_get() for RNR

## Summary
Severity: Medium
Advisory: CVE-2024-48873
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-48873
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtw89: check return value of ieee80211_probereq_get() for RNR

The return value of ieee80211_probereq_get() might be NULL, so check it
before using to avoid NULL pointer access.

Addresses-Coverity-ID: 1529805 ("Dereference null return value")

## References
- https://git.kernel.org/stable/c/1a0f54cb3fea5d087440b2bae03202c445156a8d
- https://git.kernel.org/stable/c/630d5d8f2bf6b340202b6bc2c05d794bbd8e4c1c
- https://git.kernel.org/stable/c/7296e5611adb2c619bd7bd3817ddde7ba865ef17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48873.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48873
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
