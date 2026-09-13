# [M] Bluetooth: Fix error code in chan_alloc_skb_cb()

## Summary
Severity: Medium
Advisory: CVE-2025-22007
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-22007
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <5.4.292, >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.132, >=6.2.0 <6.6.85, >=6.7.0 <6.12.21, >=6.13.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: Fix error code in chan_alloc_skb_cb()

The chan_alloc_skb_cb() function is supposed to return error pointers on
error.  Returning NULL will lead to a NULL dereference.

## References
- https://git.kernel.org/stable/c/1bd68db7beb426ab5a45d81516ed9611284affc8
- https://git.kernel.org/stable/c/72d061ee630d0dbb45c2920d8d19b3861c413e54
- https://git.kernel.org/stable/c/761b7c36addd22c7e6ceb05caaadc3b062d99faa
- https://git.kernel.org/stable/c/76304cba8cba12bb10d89d016c28403a2dd89a29
- https://git.kernel.org/stable/c/788ae2ae4cf484e248b5bc29211c7ac6510e3e92
- https://git.kernel.org/stable/c/a78692ec0d1e17a96b09f2349a028878f5b305e4
- https://git.kernel.org/stable/c/b3d607e36fef4bd05fb938a8a868ff70e9fedbe2
- https://git.kernel.org/stable/c/ecd06ad0823a90b4420c377ef8917e44e23ee841
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22007.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22007
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
