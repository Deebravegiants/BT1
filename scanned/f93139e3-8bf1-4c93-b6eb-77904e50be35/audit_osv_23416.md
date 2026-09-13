# [H] btrfs: fix use-after-free after failure to create a snapshot

## Summary
Severity: High
Advisory: CVE-2022-48733
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48733
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <5.10.226, >=5.11.0 <5.15.22, >=5.16.0 <5.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix use-after-free after failure to create a snapshot

At ioctl.c:create_snapshot(), we allocate a pending snapshot structure and
then attach it to the transaction's list of pending snapshots. After that
we call btrfs_commit_transaction(), and if that returns an error we jump
to 'fail' label, where we kfree() the pending snapshot structure. This can
result in a later use-after-free of the pending snapshot:

1) We allocated the pending snapshot and added it to the transaction's
   list of pending snapshots;

2) We call btrfs_commit_transaction(), and it fails either at the first
   call to btrfs_run_delayed_refs() or btrfs_start_dirty_block_groups().
   In both cases, we don't abort the transaction and we release our
   transaction handle. We jump to the 'fail' label and free the pending
   snapshot structure. We return with the pending snapshot still in the
   transaction's list;

3) Another task commits the transaction. This time there's no error at
   all, and then during the transaction commit it accesses a pointer
   to the pending snapshot structure that the snapshot creation task
   has already freed, resulting in a user-after-free.

This issue could actually be detected by smatch, which produced the
following warning:

  fs/btrfs/ioctl.c:843 create_snapshot() warn: '&pending_snapshot->list' not removed from list

So fix this by not having the snapshot creation ioctl directly add the
pending snapshot to the transaction's list. Instead add the pending
snapshot to the transaction handle, and then at btrfs_commit_transaction()
we add the snapshot to the list only when we can guarantee that any error
returned after that point will result in a transaction abort, in which
case the ioctl code can safely free the pending snapshot and no one can
access it anymore.

## References
- https://git.kernel.org/stable/c/28b21c558a3753171097193b6f6602a94169093a
- https://git.kernel.org/stable/c/7e4c72dbaf62f8978af8321a24dbd35566d3a78a
- https://git.kernel.org/stable/c/9372fa1d73da5f1673921e365d0cd2c27ec7adc2
- https://git.kernel.org/stable/c/a7b717fa15165d3d9245614680bebc48a52ac05d
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48733.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48733
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
