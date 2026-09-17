# [M] CVE-2023-37454

## Summary
Severity: Medium
Advisory: CVE-2023-37454
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-06
Source: https://osv.dev/vulnerability/CVE-2023-37454
Type: osv

## Details
An issue was discovered in the Linux kernel through 6.4.2. A crafted UDF filesystem image causes a use-after-free write operation in the udf_put_super and udf_close_lvid functions in fs/udf/super.c. NOTE: the suse.com reference has a different perspective about this.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6f861765464f43a71462d52026fbddfc858239a5
- https://lore.kernel.org/all/00000000000056e02f05dfb6e11a%40google.com/T/
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2023-37454
- https://syzkaller.appspot.com/bug?extid=26873a72980f8fa8bc55
- https://syzkaller.appspot.com/bug?extid=60864ed35b1073540d57
- https://syzkaller.appspot.com/bug?extid=61564e5023b7229ec85d
