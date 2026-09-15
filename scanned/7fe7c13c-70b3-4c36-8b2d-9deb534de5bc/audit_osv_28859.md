# [H] net: sched: sch_multiq: fix possible OOB write in multiq_tune()

## Summary
Severity: High
Advisory: CVE-2024-36978
Aliases: A-349777785, ASB-A-349777785
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-36978
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.279, >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: sched: sch_multiq: fix possible OOB write in multiq_tune()

q->bands will be assigned to qopt->bands to execute subsequent code logic
after kmalloc. So the old q->bands should not be used in kmalloc.
Otherwise, an out-of-bounds write will occur.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/0f208fad86631e005754606c3ec80c0d44a11882
- https://git.kernel.org/stable/c/52b1aa07cda6a199cd6754d3798c7759023bc70f
- https://git.kernel.org/stable/c/54c2c171c11a798fe887b3ff72922aa9d1411c1e
- https://git.kernel.org/stable/c/598572c64287aee0b75bbba4e2881496878860f3
- https://git.kernel.org/stable/c/affc18fdc694190ca7575b9a86632a73b9fe043d
- https://git.kernel.org/stable/c/d5d9d241786f49ae7cbc08e7fc95a115e9d80f3d
- https://git.kernel.org/stable/c/d6fb5110e8722bc00748f22caeb650fe4672f129
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36978.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36978
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
