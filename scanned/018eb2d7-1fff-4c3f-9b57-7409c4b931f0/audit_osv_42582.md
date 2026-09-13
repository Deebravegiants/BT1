# [H] wifi: mac80211: validate extension-frame layout before RX

## Summary
Severity: High
Advisory: CVE-2026-68470
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-68470
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: validate extension-frame layout before RX

Extension frames only have the extension header at the regular 802.11
header offset. The generic RX path can still reach helpers and interface
dispatch code that read regular header address fields before unsupported
extension subtypes are dropped.

mac80211 currently only handles S1G beacon extension frames. Drop other
extension subtypes before they can reach regular-header RX processing.
For S1G beacons, linearize the SKB with the management-frame path and
require the fixed S1G beacon header, including optional fixed fields
indicated by frame control, before generic RX dispatch.

Route S1G beacons through the station/default-link RX path without
regular-header station lookup. Avoid regular-header address reads in the
mac80211 RX paths that process S1G extension beacons, including
accept-frame, duplicate-detection, address-copy, and MLO
address-translation paths.

Also make ieee80211_get_bssid() length-safe before returning the S1G
source-address pointer.

## References
- https://git.kernel.org/stable/c/57d503ce32eccfa7650065ca4c560f7e29a2e676
- https://git.kernel.org/stable/c/625fc704b19cb48d7d269ad54ffffb4d3bf9c7ed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68470.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68470
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
