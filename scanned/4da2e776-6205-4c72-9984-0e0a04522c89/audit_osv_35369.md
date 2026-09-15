# [H] wifi: rtl8xxxu: fix slab-out-of-bounds in rtl8xxxu_sta_add

## Summary
Severity: High
Advisory: CVE-2025-71234
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2025-71234
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.72, >=6.13.0 <6.18.11, >=6.19.0 <6.19.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtl8xxxu: fix slab-out-of-bounds in rtl8xxxu_sta_add

The driver does not set hw->sta_data_size, which causes mac80211 to
allocate insufficient space for driver private station data in
__sta_info_alloc(). When rtl8xxxu_sta_add() accesses members of
struct rtl8xxxu_sta_info through sta->drv_priv, this results in a
slab-out-of-bounds write.

KASAN report on RISC-V (VisionFive 2) with RTL8192EU adapter:

  BUG: KASAN: slab-out-of-bounds in rtl8xxxu_sta_add+0x31c/0x346
  Write of size 8 at addr ffffffd6d3e9ae88 by task kworker/u16:0/12

Set hw->sta_data_size to sizeof(struct rtl8xxxu_sta_info) during
probe, similar to how hw->vif_data_size is configured. This ensures
mac80211 allocates sufficient space for the driver's per-station
private data.

Tested on StarFive VisionFive 2 v1.2A board.

## References
- https://git.kernel.org/stable/c/116f7bd8160c6b37d1c6939385abf90f6f6ed2f5
- https://git.kernel.org/stable/c/5d810ba377eddee95d30766d360a14efbb3d1872
- https://git.kernel.org/stable/c/86c946bcc00f6390ef65e9614ae60a9377e454f8
- https://git.kernel.org/stable/c/9a0f3fa6ecd0c9c32dbc367a57482bbf7c7d25bf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71234.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71234
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
