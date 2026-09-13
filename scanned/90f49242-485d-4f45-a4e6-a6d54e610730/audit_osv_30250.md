# [H] wifi: cfg80211: clear wdev->cqm_config pointer on free

## Summary
Severity: High
Advisory: CVE-2024-50235
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50235
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.116, >=6.2.0 <6.6.60, >=6.6.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cfg80211: clear wdev->cqm_config pointer on free

When we free wdev->cqm_config when unregistering, we also
need to clear out the pointer since the same wdev/netdev
may get re-registered in another network namespace, then
destroyed later, running this code again, which results in
a double-free.

## References
- https://git.kernel.org/stable/c/64e4c45d23cd7f6167f69cc2d2877bc7f54292e5
- https://git.kernel.org/stable/c/6c44abb2d4c3262737d5d67832daebc8cf48b8c9
- https://git.kernel.org/stable/c/ba392e1355ba74b1d4fa11b85f71ab6ed7ecc058
- https://git.kernel.org/stable/c/d5fee261dfd9e17b08b1df8471ac5d5736070917
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50235.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50235
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
