# [C] CVE-2014-3180

## Summary
Severity: Critical
Advisory: CVE-2014-3180
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-11-06
Source: https://osv.dev/vulnerability/CVE-2014-3180
Type: osv

## Details
In kernel/compat.c in the Linux kernel before 3.17, as used in Google Chrome OS and other products, there is a possible out-of-bounds read. restart_syscall uses uninitialized data when restarting compat_sys_nanosleep. NOTE: this is disputed because the code path is unreachable

## References
- https://bugs.chromium.org/p/chromium/issues/detail?id=408827
- https://lkml.org/lkml/2014/9/7/29
