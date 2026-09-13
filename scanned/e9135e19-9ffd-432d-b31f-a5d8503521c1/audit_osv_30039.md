# [C] nbd: fix race between timeout and normal completion

## Summary
Severity: Critical
Advisory: CVE-2024-49855
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49855
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

nbd: fix race between timeout and normal completion

If request timetout is handled by nbd_requeue_cmd(), normal completion
has to be stopped for avoiding to complete this requeued request, other
use-after-free can be triggered.

Fix the race by clearing NBD_CMD_INFLIGHT in nbd_requeue_cmd(), meantime
make sure that cmd->lock is grabbed for clearing the flag and the
requeue.

## References
- https://git.kernel.org/stable/c/5236ada8ebbd9e7461f17477357582f5be4f46f7
- https://git.kernel.org/stable/c/6e73b946a379a1dfbb62626af93843bdfb53753d
- https://git.kernel.org/stable/c/9a74c3e6c0d686c26ba2aab66d15ddb89dc139cc
- https://git.kernel.org/stable/c/9c25faf72d780a9c71081710cd48759d61ff6e9b
- https://git.kernel.org/stable/c/c9ea57c91f03bcad415e1a20113bdb2077bcf990
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49855.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49855
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
