# [H] wifi: wilc1000: fix u8 overflow in SSID scan buffer size calculation

## Summary
Severity: High
Advisory: CVE-2026-31780
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31780
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: wilc1000: fix u8 overflow in SSID scan buffer size calculation

The variable valuesize is declared as u8 but accumulates the total
length of all SSIDs to scan. Each SSID contributes up to 33 bytes
(IEEE80211_MAX_SSID_LEN + 1), and with WILC_MAX_NUM_PROBED_SSID (10)
SSIDs the total can reach 330, which wraps around to 74 when stored
in a u8.

This causes kmalloc to allocate only 75 bytes while the subsequent
memcpy writes up to 331 bytes into the buffer, resulting in a 256-byte
heap buffer overflow.

Widen valuesize from u8 to u32 to accommodate the full range.

## References
- https://git.kernel.org/stable/c/0c7f21d8bd2f93998b72b7a7f93152336aeca4dd
- https://git.kernel.org/stable/c/34a23fd9ddd683a03c7e8cc0ceded3e59e354b99
- https://git.kernel.org/stable/c/549f02d8ec94d39092ab6d9b103d0d6783a4b024
- https://git.kernel.org/stable/c/9907ac9b9a18b92fc34b9e4cb9e10f208dc1d3f7
- https://git.kernel.org/stable/c/bfbddeadd4779651403035ee177ae2f22f9f5521
- https://git.kernel.org/stable/c/c97b2a00059608592ad0d86fbb813a4f8cf9464b
- https://git.kernel.org/stable/c/d049e56b1739101d1c4d81deedb269c52a8dbba0
- https://git.kernel.org/stable/c/d8388614de613c28eeb659c10115060a83739924
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31780.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31780
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
