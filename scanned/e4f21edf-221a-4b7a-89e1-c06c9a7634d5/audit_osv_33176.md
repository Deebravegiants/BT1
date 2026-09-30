# [H] wifi: cfg80211: sme: cap SSID length in __cfg80211_connect_result()

## Summary
Severity: High
Advisory: CVE-2025-39849
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-39849
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.151, >=6.2.0 <6.6.105, >=6.3.0 <6.12.46, >=6.7.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cfg80211: sme: cap SSID length in __cfg80211_connect_result()

If the ssid->datalen is more than IEEE80211_MAX_SSID_LEN (32) it would
lead to memory corruption so add some bounds checking.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/31229145e6ba5ace3e9391113376fa05b7831ede
- https://git.kernel.org/stable/c/5cb7cab7adf9b1e6a99e2081b0e30e9e59d07523
- https://git.kernel.org/stable/c/62b635dcd69c4fde7ce1de4992d71420a37e51e3
- https://git.kernel.org/stable/c/8e751d46336205abc259ed3990e850a9843fb649
- https://git.kernel.org/stable/c/e472f59d02c82b511bc43a3f96d62ed08bf4537f
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39849.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39849
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
