# [H] net_sched: qfq: Fix double list add in class with netem as child qdisc

## Summary
Severity: High
Advisory: CVE-2025-37913
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37913
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.294, >=5.5.0 <5.10.238, >=5.11.0 <5.15.182, >=5.16.0 <6.1.138, >=6.2.0 <6.6.90, >=6.7.0 <6.12.28, >=6.13.0 <6.14.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net_sched: qfq: Fix double list add in class with netem as child qdisc

As described in Gerrard's report [1], there are use cases where a netem
child qdisc will make the parent qdisc's enqueue callback reentrant.
In the case of qfq, there won't be a UAF, but the code will add the same
classifier to the list twice, which will cause memory corruption.

This patch checks whether the class was already added to the agg->active
list (cl_is_active) before doing the addition to cater for the reentrant
case.

[1] https://lore.kernel.org/netdev/CAHcdcOm+03OD2j6R0=YHKqmy=VgJ8xEOKuP6c7mSgnp-TEJJbw@mail.gmail.com/

## References
- https://git.kernel.org/stable/c/005a479540478a820c52de098e5e767e63e36f0a
- https://git.kernel.org/stable/c/041f410aec2c1751ee22b8b73ba05d38c3a6a602
- https://git.kernel.org/stable/c/0aa23e0856b7cedb3c88d8e3d281c212c7e4fbeb
- https://git.kernel.org/stable/c/0bf32d6fb1fcbf841bb9945570e0e2a70072c00f
- https://git.kernel.org/stable/c/370218e8ce711684acc4cdd3cc3c6dd7956bc165
- https://git.kernel.org/stable/c/53bc0b55178bd59bdd4bcd16349505cabf54b1a2
- https://git.kernel.org/stable/c/a43783119e01849fbf2fe8855634e8989b240cb4
- https://git.kernel.org/stable/c/f139f37dcdf34b67f5bf92bc8e0f7f6b3ac63aa4
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37913.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37913
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
