# [M] md: Don't suspend the array for interrupted reshape

## Summary
Severity: Medium
Advisory: CVE-2024-26755
Ecosystem: Linux
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26755
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

md: Don't suspend the array for interrupted reshape

md_start_sync() will suspend the array if there are spares that can be
added or removed from conf, however, if reshape is still in progress,
this won't happen at all or data will be corrupted(remove_and_add_spares
won't be called from md_choose_sync_action for reshape), hence there is
no need to suspend the array if reshape is not done yet.

Meanwhile, there is a potential deadlock for raid456:

1) reshape is interrupted;

2) set one of the disk WantReplacement, and add a new disk to the array,
   however, recovery won't start until the reshape is finished;

3) then issue an IO across reshpae position, this IO will wait for
   reshape to make progress;

4) continue to reshape, then md_start_sync() found there is a spare disk
   that can be added to conf, mddev_suspend() is called;

Step 4 and step 3 is waiting for each other, deadlock triggered. Noted
this problem is found by code review, and it's not reporduced yet.

Fix this porblem by don't suspend the array for interrupted reshape,
this is safe because conf won't be changed until reshape is done.

## References
- https://git.kernel.org/stable/c/60d6130d0ac1d883ed93c2a1e10aadb60967fd48
- https://git.kernel.org/stable/c/9e46c70e829bddc24e04f963471e9983a11598b7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26755.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26755
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
