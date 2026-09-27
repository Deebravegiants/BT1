# [H] net_sched: hfsc: Fix a potential UAF in hfsc_dequeue() too

## Summary
Severity: High
Advisory: CVE-2025-37823
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-08
Source: https://osv.dev/vulnerability/CVE-2025-37823
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.293, >=5.5.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.136, >=6.2.0 <6.6.89, >=6.7.0 <6.12.26, >=6.13.0 <6.14.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net_sched: hfsc: Fix a potential UAF in hfsc_dequeue() too

Similarly to the previous patch, we need to safe guard hfsc_dequeue()
too. But for this one, we don't have a reliable reproducer.

## References
- https://git.kernel.org/stable/c/11bccb054c1462fb069219f8e98e97a5a730758e
- https://git.kernel.org/stable/c/2f46d14919c39528c6e540ebc43f90055993eedc
- https://git.kernel.org/stable/c/68f256305ceb426d545a0dc31f83c2ab1d211a1e
- https://git.kernel.org/stable/c/6ccbda44e2cc3d26fd22af54c650d6d5d801addf
- https://git.kernel.org/stable/c/76c4c22c2437d3d3880efc0f62eca06ef078d290
- https://git.kernel.org/stable/c/c6936266f8bf98a53f28ef9a820e6a501e946d09
- https://git.kernel.org/stable/c/c6f035044104c6ff656f4565cd22938dc892528c
- https://git.kernel.org/stable/c/da7936518996d290e2fcfcaf6cd7e15bfd87804a
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37823.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37823
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
