# [H] CVE-2020-36387

## Summary
Severity: High
Advisory: CVE-2020-36387
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-07
Source: https://osv.dev/vulnerability/CVE-2020-36387
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.8.2. fs/io_uring.c has a use-after-free related to io_async_task_func and ctx reference holding, aka CID-6d816e088c35.

## References
- https://security.netapp.com/advisory/ntap-20210727-0006/
- https://sites.google.com/view/syzscope/kasan-use-after-free-read-in-io_async_task_func
- https://syzkaller.appspot.com/bug?id=ce5f07d6ec3b5050b8f0728a3b389aa510f2591b
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.2
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6d816e088c359866f9867057e04f244c608c42fe
