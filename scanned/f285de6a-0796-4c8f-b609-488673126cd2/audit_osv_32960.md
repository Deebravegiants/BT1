# [C] nfsd: nfsd4_spo_must_allow() must check this is a v4 compound request

## Summary
Severity: Critical
Advisory: CVE-2025-38430
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38430
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.4.295, >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: nfsd4_spo_must_allow() must check this is a v4 compound request

If the request being processed is not a v4 compound request, then
examining the cstate can have undefined results.

This patch adds a check that the rpc procedure being executed
(rq_procinfo) is the NFSPROC4_COMPOUND procedure.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/1244f0b2c3cecd3f349a877006e67c9492b41807
- https://git.kernel.org/stable/c/2c54bd5a380ebf646fb9efbc4ae782ff3a83a5af
- https://git.kernel.org/stable/c/425efc6b3292a3c79bfee4a1661cf043dcd9cf2f
- https://git.kernel.org/stable/c/64a723b0281ecaa59d31aad73ef8e408a84cb603
- https://git.kernel.org/stable/c/7a75a956692aa64211a9e95781af1ec461642de4
- https://git.kernel.org/stable/c/b1d0323a09a29f81572c7391e0d80d78724729c9
- https://git.kernel.org/stable/c/bf78a2706ce975981eb5167f2d3b609eb5d24c19
- https://git.kernel.org/stable/c/e7e943ddd1c6731812357a28e7954ade3a7d8517
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38430.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38430
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
