# [H] forcedeth: fix UAF of txrx_stats in nv_remove

## Summary
Severity: High
Advisory: CVE-2026-74548
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74548
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

forcedeth: fix UAF of txrx_stats in nv_remove

nv_remove() frees the per-CPU txrx_stats before unregister_netdev().
Until unregister completes, ndo_get_stats64, the NAPI/xmit data path,
and nv_close()/drain may still access txrx_stats, leading to a
use-after-free.

Free the stats only after unregister_netdev().

## References
- https://git.kernel.org/stable/c/201e05aa531eba0dfe2ee05b4e178f6ffa12c8b1
- https://git.kernel.org/stable/c/22666ba1420164753d7b0f5a841986b25ace5435
- https://git.kernel.org/stable/c/7c22b4ee0bd003cecfc14ca28981cb213e201f70
- https://git.kernel.org/stable/c/ae20a8a4de06a289d40b0a0633d8d573f1fcb049
- https://git.kernel.org/stable/c/c9d24a205fd508b9999fcab6aca4c590490a12cf
- https://git.kernel.org/stable/c/cdf864d5d3c813ae1876f2bacc1cf3ac3c66dfc9
- https://git.kernel.org/stable/c/cf2dcde2284562ff87830ca0b7fa2b06e95aef1e
- https://git.kernel.org/stable/c/d51ce7a63b76eda02cabfed1b0cc277b2f5c9bcc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74548.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74548
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
