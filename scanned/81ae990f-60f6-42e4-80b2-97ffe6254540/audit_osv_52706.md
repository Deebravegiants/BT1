# [M] CVE-2022-0480

## Summary
Severity: Medium
Advisory: CVE-2022-0480
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-29
Source: https://osv.dev/vulnerability/CVE-2022-0480
Type: osv

## Details
A flaw was found in the filelock_init in fs/locks.c function in the Linux kernel. This issue can lead to host memory exhaustion due to memcg not limiting the number of Portable Operating System Interface (POSIX) file locks.

## References
- https://access.redhat.com/security/cve/CVE-2022-0480
- https://lore.kernel.org/linux-mm/20210902215519.AWcuVc3li%25akpm%40linux-foundation.org/
- https://ubuntu.com/security/CVE-2022-0480
- https://bugzilla.redhat.com/show_bug.cgi?id=2049700
- https://github.com/kata-containers/kata-containers/issues/3373
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=0f12156dff2862ac54235fc72703f18770769042
