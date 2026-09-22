# [M] fs/proc: fix softlockup in __read_vmcore (part 2)

## Summary
Severity: Medium
Advisory: CVE-2025-21694
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-12
Source: https://osv.dev/vulnerability/CVE-2025-21694
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.290, >=5.5.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.127, >=6.2.0 <6.6.74, >=6.7.0 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/proc: fix softlockup in __read_vmcore (part 2)

Since commit 5cbcb62dddf5 ("fs/proc: fix softlockup in __read_vmcore") the
number of softlockups in __read_vmcore at kdump time have gone down, but
they still happen sometimes.

In a memory constrained environment like the kdump image, a softlockup is
not just a harmless message, but it can interfere with things like RCU
freeing memory, causing the crashdump to get stuck.

The second loop in __read_vmcore has a lot more opportunities for natural
sleep points, like scheduling out while waiting for a data write to
happen, but apparently that is not always enough.

Add a cond_resched() to the second loop in __read_vmcore to (hopefully)
get rid of the softlockups.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://git.kernel.org/stable/c/649b266606bc413407ce315f710c8ce8a88ee30a
- https://git.kernel.org/stable/c/65c367bd9d4f43513c7f837df5753bea9561b836
- https://git.kernel.org/stable/c/80828540dad0757b6337c6561d49c81038f38d87
- https://git.kernel.org/stable/c/80da29deb88a3a907441fc35bb7bac309f31e713
- https://git.kernel.org/stable/c/84c4ed15626574c9ac6c1039ba9c137a77bcc7f2
- https://git.kernel.org/stable/c/a5a2ee8144c3897d37403a69118c3e3dc5713958
- https://git.kernel.org/stable/c/cbc5dde0a461240046e8a41c43d7c3b76d5db952
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21694.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21694
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
