# [H] CVE-2021-47342

## Summary
Severity: High
Advisory: CVE-2021-47342
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47342
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix possible UAF when remounting r/o a mmp-protected file system

After commit 618f003199c6 ("ext4: fix memory leak in
ext4_fill_super"), after the file system is remounted read-only, there
is a race where the kmmpd thread can exit, causing sbi->s_mmp_tsk to
point at freed memory, which the call to ext4_stop_mmpd() can trip
over.

Fix this by only allowing kmmpd() to exit when it is stopped via
ext4_stop_mmpd().

Bug-Report-Link: <20210629143603.2166962-1-yebin10@huawei.com>

## References
- https://git.kernel.org/stable/c/61bb4a1c417e5b95d9edb4f887f131de32e419cb
- https://git.kernel.org/stable/c/7ed572cdf11081f8f9e07abd4bea56a3f2c4edbd
- https://git.kernel.org/stable/c/b663890d854403e566169f7e90aed5cd6ff64f6b
