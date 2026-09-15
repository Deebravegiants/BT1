# [H] platform/x86: ISST: Restore SST-PP control to all domains

## Summary
Severity: High
Advisory: CVE-2026-72143
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72143
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86: ISST: Restore SST-PP control to all domains

The SST-PP control offset is only restored to power domain 0 after
resume. During suspend, control values are read and stored for all
power domains.

Use pd_info->sst_base instead of power_domain_info->sst_base, which
only points to power domain 0 base address.

## References
- https://git.kernel.org/stable/c/2565a28cdcdcb035e151d285efcba26bccb3726e
- https://git.kernel.org/stable/c/2a42f651cce91e9cbe65fe933622c522cbb1868b
- https://git.kernel.org/stable/c/cea03d67db3a880893360bdbb1b0b8d9b33b1799
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72143.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72143
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
