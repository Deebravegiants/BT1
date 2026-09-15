# [H] wifi: rtw89: add bounds check on firmware mac_id in link lookup

## Summary
Severity: High
Advisory: CVE-2026-74409
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74409
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtw89: add bounds check on firmware mac_id in link lookup

The mac_id field in RX descriptors is 8 bits wide (0-255), but
assoc_link_on_macid[] has only RTW89_MAX_MAC_ID_NUM (128) entries.
While the driver currently assigns mac_id values below 128, the
descriptor value comes from firmware and is not validated before use
as an array index. Add a defensive bounds check in
rtw89_assoc_link_rcu_dereference() to guard against out-of-range
firmware values.

## References
- https://git.kernel.org/stable/c/6d88244bb129755acca696f9227200f4a2d106a6
- https://git.kernel.org/stable/c/920101305e7601a33b9e01019f4ca526af2526ae
- https://git.kernel.org/stable/c/ad445de67359f24088d4305c05fbd7e34c4e35e3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74409.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74409
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
