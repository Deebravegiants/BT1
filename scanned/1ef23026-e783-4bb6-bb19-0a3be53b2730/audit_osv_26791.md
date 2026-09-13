# [H] SMB3: Add missing locks to protect deferred close file list

## Summary
Severity: High
Advisory: CVE-2023-53990
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-53990
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.111, >=5.16.0 <6.1.28, >=6.0.0 <6.2.15, >=6.2.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

SMB3: Add missing locks to protect deferred close file list

cifs_del_deferred_close function has a critical section which modifies
the deferred close file list. We must acquire deferred_lock before
calling cifs_del_deferred_close function.

## References
- https://git.kernel.org/stable/c/0f87e18203bd30f71eb1a65259e28e291b6cc43a
- https://git.kernel.org/stable/c/32a046ccaeea6c19965c04a4c521e703f6607924
- https://git.kernel.org/stable/c/3aa9d065b0685b4e6052f3f2a2462966fdc44fd2
- https://git.kernel.org/stable/c/ab9ddc87a9055c4bebd6524d5d761d605d52e557
- https://git.kernel.org/stable/c/cb36365dac25d546ca4af0eb22acb43c9b4ddfdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53990.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53990
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
