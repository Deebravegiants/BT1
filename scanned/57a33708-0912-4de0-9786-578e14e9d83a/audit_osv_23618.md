# [M] mt76: mt7915: fix possible memory leak in mt7915_mcu_add_sta

## Summary
Severity: Medium
Advisory: CVE-2022-49230
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49230
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

mt76: mt7915: fix possible memory leak in mt7915_mcu_add_sta

Free allocated skb in mt7915_mcu_add_sta routine in case of failures.

## References
- https://git.kernel.org/stable/c/a43736cd12d82913102eb49cb56787a5553e028f
- https://git.kernel.org/stable/c/b334a245ff1d76b1e97af8cea648ea6798b9eb87
- https://git.kernel.org/stable/c/daf02c7e3c3dc82ffa925999597bd455cf799551
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49230.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49230
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
