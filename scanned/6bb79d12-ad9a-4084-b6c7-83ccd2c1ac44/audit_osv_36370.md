# [H] wifi: mac80211: bounds-check link_id in ieee80211_ml_reconfiguration

## Summary
Severity: High
Advisory: CVE-2026-23246
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-23246
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.130, >=6.7.0 <6.12.77, >=6.13.0 <6.18.17, >=6.19.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: bounds-check link_id in ieee80211_ml_reconfiguration

link_id is taken from the ML Reconfiguration element (control & 0x000f),
so it can be 0..15. link_removal_timeout[] has IEEE80211_MLD_MAX_NUM_LINKS
(15) elements, so index 15 is out-of-bounds. Skip subelements with
link_id >= IEEE80211_MLD_MAX_NUM_LINKS to avoid a stack out-of-bounds
write.

## References
- https://git.kernel.org/stable/c/162d331d833dc73a3e905a24c44dd33732af1fc5
- https://git.kernel.org/stable/c/650981e718e68005ca2760a6358134b8a98ebea4
- https://git.kernel.org/stable/c/bfde158d5d1322c0c2df398a8d1ccce04943be2e
- https://git.kernel.org/stable/c/d58d71c2167601762351962b9604808d3be94400
- https://git.kernel.org/stable/c/f35ceec54d48e227fa46f8f97fd100a77b8eab15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23246.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23246
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
