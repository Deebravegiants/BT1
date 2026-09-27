# [H] nvme-tcp: fix the memleak while create new ctrl failed

## Summary
Severity: High
Advisory: CVE-2024-56632
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56632
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-tcp: fix the memleak while create new ctrl failed

Now while we create new ctrl failed, we have not free the
tagset occupied by admin_q, here try to fix it.

## References
- https://git.kernel.org/stable/c/ceff9ac13a2478afddce85414d404e6aff6425f6
- https://git.kernel.org/stable/c/fec55c29e54d3ca6fe9d7d7d9266098b4514fd34
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56632.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56632
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
