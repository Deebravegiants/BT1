# [H] f2fs: Require FMODE_WRITE for atomic write ioctls

## Summary
Severity: High
Advisory: CVE-2024-47740
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47740
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: Require FMODE_WRITE for atomic write ioctls

The F2FS ioctls for starting and committing atomic writes check for
inode_owner_or_capable(), but this does not give LSMs like SELinux or
Landlock an opportunity to deny the write access - if the caller's FSUID
matches the inode's UID, inode_owner_or_capable() immediately returns true.

There are scenarios where LSMs want to deny a process the ability to write
particular files, even files that the FSUID of the process owns; but this
can currently partially be bypassed using atomic write ioctls in two ways:

 - F2FS_IOC_START_ATOMIC_REPLACE + F2FS_IOC_COMMIT_ATOMIC_WRITE can
   truncate an inode to size 0
 - F2FS_IOC_START_ATOMIC_WRITE + F2FS_IOC_ABORT_ATOMIC_WRITE can revert
   changes another process concurrently made to a file

Fix it by requiring FMODE_WRITE for these operations, just like for
F2FS_IOC_MOVE_RANGE. Since any legitimate caller should only be using these
ioctls when intending to write into the file, that seems unlikely to break
anything.

## References
- https://git.kernel.org/stable/c/000bab8753ae29a259feb339b99ee759795a48ac
- https://git.kernel.org/stable/c/32f348ecc149e9ca70a1c424ae8fa9b6919d2713
- https://git.kernel.org/stable/c/4583290898c13c2c2e5eb8773886d153c2c5121d
- https://git.kernel.org/stable/c/4ce87674c3a6b4d3b3d45f85b584ab8618a3cece
- https://git.kernel.org/stable/c/4f5a100f87f32cb65d4bb1ad282a08c92f6f591e
- https://git.kernel.org/stable/c/5e0de753bfe87768ebe6744d869caa92f35e5731
- https://git.kernel.org/stable/c/700f3a7c7fa5764c9f24bbf7c78e0b6e479fa653
- https://git.kernel.org/stable/c/88ff021e1fea2d9b40b2d5efd9013c89f7be04ac
- https://git.kernel.org/stable/c/f3bfac2cabf5333506b263bc0c8497c95302f32d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47740.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47740
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
