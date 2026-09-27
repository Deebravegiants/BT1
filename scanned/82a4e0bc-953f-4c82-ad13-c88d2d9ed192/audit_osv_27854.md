# [M] scsi: core: Move scsi_host_busy() out of host lock for waking up EH handler

## Summary
Severity: Medium
Advisory: CVE-2024-26627
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-06
Source: https://osv.dev/vulnerability/CVE-2024-26627
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.77, >=6.2.0 <6.6.16, >=6.7.0 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: core: Move scsi_host_busy() out of host lock for waking up EH handler

Inside scsi_eh_wakeup(), scsi_host_busy() is called & checked with host
lock every time for deciding if error handler kthread needs to be waken up.

This can be too heavy in case of recovery, such as:

 - N hardware queues

 - queue depth is M for each hardware queue

 - each scsi_host_busy() iterates over (N * M) tag/requests

If recovery is triggered in case that all requests are in-flight, each
scsi_eh_wakeup() is strictly serialized, when scsi_eh_wakeup() is called
for the last in-flight request, scsi_host_busy() has been run for (N * M -
1) times, and request has been iterated for (N*M - 1) * (N * M) times.

If both N and M are big enough, hard lockup can be triggered on acquiring
host lock, and it is observed on mpi3mr(128 hw queues, queue depth 8169).

Fix the issue by calling scsi_host_busy() outside the host lock. We don't
need the host lock for getting busy count because host the lock never
covers that.

[mkp: Drop unnecessary 'busy' variables pointed out by Bart]

## References
- https://git.kernel.org/stable/c/07e3ca0f17f579491b5f54e9ed05173d6c1d6fcb
- https://git.kernel.org/stable/c/4373534a9850627a2695317944898eb1283a2db0
- https://git.kernel.org/stable/c/65ead8468c21c2676d4d06f50b46beffdea69df1
- https://git.kernel.org/stable/c/d37c1c81419fdef66ebd0747cf76fb8b7d979059
- https://git.kernel.org/stable/c/db6338f45971b4285ea368432a84033690eaf53c
- https://git.kernel.org/stable/c/f5944853f7a961fedc1227dc8f60393f8936d37c
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26627.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26627
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
