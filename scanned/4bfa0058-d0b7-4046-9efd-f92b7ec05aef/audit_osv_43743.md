# [H] net/sched: reject overly deep qdisc hierarchies

## Summary
Severity: High
Advisory: CVE-2026-74663
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74663
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.267, >=5.11.0 <5.15.218, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: reject overly deep qdisc hierarchies

Deep qdisc hierarchies can lead to excessive recursion in qdisc tree
walkers and exhaust the kernel stack. The existing loop check does not
cover the create-and-graft path, so a hierarchy can still be extended by
creating a new child qdisc below an already deep parent.

Store the hierarchy depth in struct Qdisc and update it when qdiscs are
grafted. Reject new child qdiscs once the parent is already at the maximum
allowed depth.

## References
- https://git.kernel.org/stable/c/08dc49df1527b09d9ea225a7265bbf6c237097bf
- https://git.kernel.org/stable/c/2759acf08a3454866660edcd3ef4e64139f254a6
- https://git.kernel.org/stable/c/8ca8cdb74939581339e1ae370193c0adb5a85336
- https://git.kernel.org/stable/c/9f69bb9fdaa2fe64b68bb62fb84d405784bee540
- https://git.kernel.org/stable/c/a4b14a4df29d36458a943f9b521ddd0f940363cc
- https://git.kernel.org/stable/c/a627d36c2a94e18c8c105ae68008786dfd85592e
- https://git.kernel.org/stable/c/dedd34b0f2310e28c5f6d4875cfbf4b7ed821c01
- https://git.kernel.org/stable/c/e2d658c6427844cee5bc654b436ca68d680b6148
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74663.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74663
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
