# [M] blk-mq: fix NULL dereference on q->elevator in blk_mq_elv_switch_none

## Summary
Severity: Medium
Advisory: CVE-2023-53292
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53292
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.175, >=6.2.0 <6.4.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

blk-mq: fix NULL dereference on q->elevator in blk_mq_elv_switch_none

After grabbing q->sysfs_lock, q->elevator may become NULL because of
elevator switch.

Fix the NULL dereference on q->elevator by checking it with lock.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/245165658e1c9f95c0fecfe02b9b1ebd30a1198a
- https://git.kernel.org/stable/c/3e977386521b71471e66ec2ba82efdfcc456adf2
- https://git.kernel.org/stable/c/988ddb77218d3975dd13dee7bb0e1fae098a9fdb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53292.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53292
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
