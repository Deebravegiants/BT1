# [H] wifi: cfg80211: fix use-after-free in cmp_bss()

## Summary
Severity: High
Advisory: CVE-2025-39864
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-39864
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.299, >=5.5.0 <5.10.243, >=5.11.0 <5.15.192, >=5.16.0 <6.1.151, >=6.2.0 <6.6.105, >=6.7.0 <6.12.46, >=6.13.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cfg80211: fix use-after-free in cmp_bss()

Following bss_free() quirk introduced in commit 776b3580178f
("cfg80211: track hidden SSID networks properly"), adjust
cfg80211_update_known_bss() to free the last beacon frame
elements only if they're not shared via the corresponding
'hidden_beacon_bss' pointer.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-089022.html
- https://git.kernel.org/stable/c/26e84445f02ce6b2fe5f3e0e28ff7add77f35e08
- https://git.kernel.org/stable/c/5b7ae04969f822283a95c866967e42b4d75e0eef
- https://git.kernel.org/stable/c/6854476d9e1aeaaf05ebc98d610061c2075db07d
- https://git.kernel.org/stable/c/912c4b66bef713a20775cfbf3b5e9bd71525c716
- https://git.kernel.org/stable/c/a8bb681e879ca3c9f722aa08d3d7ae41c42a8807
- https://git.kernel.org/stable/c/a97a9791e455bb0cd5e7a38b5abcb05523d4e21c
- https://git.kernel.org/stable/c/b7d08929178c16398278613df07ad65cf63cce9d
- https://git.kernel.org/stable/c/ff040562c10a540b8d851f7f4145fa112977f853
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39864.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39864
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
