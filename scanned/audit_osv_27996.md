# [H] crypto: iaa - Fix nr_cpus < nr_iaa case

## Summary
Severity: High
Advisory: CVE-2024-26945
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26945
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: iaa - Fix nr_cpus < nr_iaa case

If nr_cpus < nr_iaa, the calculated cpus_per_iaa will be 0, which
causes a divide-by-0 in rebalance_wq_table().

Make sure cpus_per_iaa is 1 in that case, and also in the nr_iaa == 0
case, even though cpus_per_iaa is never used if nr_iaa == 0, for
paranoia.

## References
- https://git.kernel.org/stable/c/5a7e89d3315d1be86aff8a8bf849023cda6547f7
- https://git.kernel.org/stable/c/a5ca1be7f9817de4e93085778b3ee2219bdc2664
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26945.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26945
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
