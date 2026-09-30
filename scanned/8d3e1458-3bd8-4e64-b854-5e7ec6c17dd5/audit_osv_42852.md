# [H] dibs: loopback: validate offset and size in move_data()

## Summary
Severity: High
Advisory: CVE-2026-72018
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72018
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dibs: loopback: validate offset and size in move_data()

The loopback move_data() performs a memcpy into the registered DMB
without checking whether offset + size exceeds the DMB length.  Unlike
real ISM hardware, which enforces memory region bounds natively, the
software loopback has no such protection.

A peer-supplied out-of-bounds offset or oversized write would result in
an OOB write past the allocated kernel buffer.  Add an explicit bounds
check before the memcpy to reject such requests with -EINVAL.

## References
- https://git.kernel.org/stable/c/78237e3c0720fcc6eb9b87e90fd70f63eeca886f
- https://git.kernel.org/stable/c/94fe0ab01b480b52bd8f977edbd845ef375d69fd
- https://git.kernel.org/stable/c/b2f426a9a22886071966432ede8fceafffe12b8c
- https://git.kernel.org/stable/c/ee188a6b264b71315a67f1b9470faad308b730d2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72018.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72018
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
