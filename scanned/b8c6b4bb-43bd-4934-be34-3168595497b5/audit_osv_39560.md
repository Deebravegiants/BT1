# [H] wifi: mac80211: drop stray 'static' from fast-RX rx_result

## Summary
Severity: High
Advisory: CVE-2026-46152
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46152
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: drop stray 'static' from fast-RX rx_result

ieee80211_invoke_fast_rx() is documented as safe for parallel RX, but
its per-invocation rx_result is declared static. Concurrent callers then
share one instance and can overwrite each other's result between
ieee80211_rx_mesh_data() and the switch on res.

That can make a packet that was queued or consumed by
ieee80211_rx_mesh_data() fall through into ieee80211_rx_8023(), or make
a packet that should continue return as queued.

Make res an automatic variable so each invocation keeps its own result.

## References
- https://git.kernel.org/stable/c/03584528bfffb195e384698af9148b94e42e3f14
- https://git.kernel.org/stable/c/1739fc31b4de06c5c78ce0741182770fb079091e
- https://git.kernel.org/stable/c/3ef44f96ccc3e06e059dec57842e366f0c4b1893
- https://git.kernel.org/stable/c/7a5b81e0c87a075afd572f659d8eb68c9c4cd2ba
- https://git.kernel.org/stable/c/e131562d6f2b958148c35c98831b007f47f0e3d3
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46152.json
- https://access.redhat.com/errata/RHSA-2026:26427
- https://access.redhat.com/errata/RHSA-2026:26428
- https://access.redhat.com/errata/RHSA-2026:27288
- https://access.redhat.com/errata/RHSA-2026:27789
- https://access.redhat.com/errata/RHSA-2026:36767
- https://access.redhat.com/errata/RHSA-2026:38902
- https://access.redhat.com/errata/RHSA-2026:44694
- https://access.redhat.com/security/cve/CVE-2026-46152
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46152.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46152
- https://bugzilla.redhat.com/show_bug.cgi?id=2482563
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
